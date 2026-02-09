import { useState, useEffect, useRef, useCallback } from 'react'
import { toPng } from 'html-to-image'
import { UnionWin } from '../types'

type TimePeriod = 'week' | 'month' | 'year'

interface InfographicData {
    wins: UnionWin[]
    totalCount: number
    topUnions: { name: string; count: number }[]
    topWinTypes: { type: string; count: number }[]
    allWinTypes: { type: string; count: number }[]
    recentPayRises: UnionWin[]
    periodLabel: string
    periodDates: string
    avgPerWeek: number
    uniqueUnions: number
}

interface AdminInfographicsProps {
    adminPassword: string
}

function getDateRange(period: TimePeriod): { start: Date; end: Date; label: string; dates: string } {
    const end = new Date()
    const start = new Date()

    const formatDate = (d: Date) => d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })

    switch (period) {
        case 'week':
            start.setDate(end.getDate() - 7)
            return {
                start,
                end,
                label: 'This Week',
                dates: `${formatDate(start)} - ${formatDate(end)}`
            }
        case 'month':
            start.setMonth(end.getMonth() - 1)
            return {
                start,
                end,
                label: 'This Month',
                dates: `${formatDate(start)} - ${formatDate(end)}`
            }
        case 'year':
            start.setFullYear(end.getFullYear() - 1)
            return {
                start,
                end,
                label: 'This Year',
                dates: `${formatDate(start)} - ${formatDate(end)}`
            }
    }
}

function aggregateWinData(wins: UnionWin[], period: TimePeriod): InfographicData {
    const { label, dates, start, end } = getDateRange(period)

    // Count wins by union
    const unionCounts = new Map<string, number>()
    wins.forEach(win => {
        const union = win.union_name ?? 'Unknown'
        unionCounts.set(union, (unionCounts.get(union) ?? 0) + 1)
    })

    // Count wins by type
    const typeCounts = new Map<string, number>()
    wins.forEach(win => {
        const types = win.win_types?.split(',').map(t => t.trim()) ?? ['Other']
        types.forEach(type => {
            typeCounts.set(type, (typeCounts.get(type) ?? 0) + 1)
        })
    })

    const allUnions = Array.from(unionCounts.entries())
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)

    const topUnions = allUnions.slice(0, 5)

    const allWinTypes = Array.from(typeCounts.entries())
        .map(([type, count]) => ({ type, count }))
        .sort((a, b) => b.count - a.count)

    const topWinTypes = allWinTypes.slice(0, 5)

    // Calculate average per week
    const daysDiff = Math.max(1, Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)))
    const weeksDiff = Math.max(1, daysDiff / 7)
    const avgPerWeek = Math.round((wins.length / weeksDiff) * 10) / 10

    // Get 3 most recent pay rises
    const recentPayRises = wins
        .filter(win => win.win_types?.toLowerCase().includes('pay rise'))
        .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
        .slice(0, 3)

    return {
        wins,
        totalCount: wins.length,
        topUnions,
        topWinTypes,
        allWinTypes,
        recentPayRises,
        periodLabel: label,
        periodDates: dates,
        avgPerWeek,
        uniqueUnions: allUnions.length
    }
}

interface InfographicCardProps {
    data: InfographicData
    period: TimePeriod
}

// Instagram post is 1080x1080 pixels, we'll render at 400x400 for preview
interface PostCardProps {
    win: UnionWin
    index: number
}

const UPLOAD_POST_API_KEY = import.meta.env.VITE_UPLOAD_POST_API_KEY || ''
const UPLOAD_POST_USER = 'whathaveunionsdoneforus'

function PostCard({ win, index }: PostCardProps) {
    const cardRef = useRef<HTMLDivElement>(null)
    const [downloading, setDownloading] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle')
    const [proxyImageUrl, setProxyImageUrl] = useState<string | null>(null)

    // Load Google Font for the card
    useEffect(() => {
        const link = document.createElement('link')
        link.href = 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap'
        link.rel = 'stylesheet'
        document.head.appendChild(link)
        return () => {
            document.head.removeChild(link)
        }
    }, [])

    // Load image through proxy and convert to base64 for download compatibility
    useEffect(() => {
        if (!win.image_urls || win.image_urls.length === 0) return

        const loadImageViaProxy = async () => {
            try {
                const proxyUrl = `/api/proxy/image?url=${encodeURIComponent(win.image_urls![0])}`
                const response = await fetch(proxyUrl)

                if (!response.ok) {
                    console.log('Proxy failed, image will use gradient background')
                    return
                }

                const blob = await response.blob()
                const reader = new FileReader()
                reader.onloadend = () => {
                    setProxyImageUrl(reader.result as string)
                }
                reader.readAsDataURL(blob)
            } catch (error) {
                console.log('Failed to load image via proxy:', error)
            }
        }

        loadImageViaProxy()
    }, [win.image_urls])

    const downloadAsImage = useCallback(async () => {
        if (!cardRef.current) return

        setDownloading(true)
        try {
            const dataUrl = await toPng(cardRef.current, {
                quality: 1,
                pixelRatio: 4, // 400 * 4 = 1600 for high resolution
                backgroundColor: '#ffffff',
                skipFonts: true // Skip font embedding to avoid CORS errors with Google Fonts
            })

            const link = document.createElement('a')
            link.download = `union-win-${win.id}-${new Date().toISOString().split('T')[0]}.png`
            link.href = dataUrl
            link.click()
        } catch (error) {
            console.error('Failed to generate image:', error)
        } finally {
            setDownloading(false)
        }
    }, [win.id])

    const uploadToInstagram = useCallback(async () => {
        if (!cardRef.current) return

        setUploading(true)
        setUploadStatus('idle')
        try {
            const dataUrl = await toPng(cardRef.current, {
                quality: 1,
                pixelRatio: 4, // 400 * 4 = 1600 for high resolution
                backgroundColor: '#ffffff',
                skipFonts: true // Skip font embedding to avoid CORS errors with Google Fonts
            })

            // Convert data URL to Blob
            const response = await fetch(dataUrl)
            const blob = await response.blob()

            // Create FormData for the API request
            const formData = new FormData()
            formData.append('photos[]', blob, `union-win-${win.id}.png`)
            formData.append('user', UPLOAD_POST_USER)
            formData.append('platform[]', 'instagram')
            formData.append('title', `✊ Union Win: ${win.summary}\n\n🏛️ ${win.union_name ?? 'Workers United'}\n\n🔗 whathaveunionsdoneforus.uk\n\n#UnionWins #WhatHaveUnionsDoneForUs`)

            const uploadResponse = await fetch('https://api.upload-post.com/api/upload_photos', {
                method: 'POST',
                headers: {
                    'Authorization': `Apikey ${UPLOAD_POST_API_KEY}`
                },
                body: formData
            })

            const result = await uploadResponse.json()

            if (result.success) {
                setUploadStatus('success')
                console.log('Upload successful:', result)
            } else {
                setUploadStatus('error')
                console.error('Upload failed:', result)
            }
        } catch (error) {
            setUploadStatus('error')
            console.error('Failed to upload to Instagram:', error)
        } finally {
            setUploading(false)
            // Reset status after 3 seconds
            setTimeout(() => setUploadStatus('idle'), 3000)
        }
    }, [win.id, win.summary, win.union_name])

    // Rotate through gradient colors
    const gradientColors = [
        { background: 'linear-gradient(135deg, #f97316, #dc2626)' }, // orange-red
        { background: 'linear-gradient(135deg, #3b82f6, #9333ea)' }, // blue-purple
        { background: 'linear-gradient(135deg, #22c55e, #14b8a6)' }, // green-teal
        { background: 'linear-gradient(135deg, #ec4899, #8b5cf6)' }, // pink-purple
        { background: 'linear-gradient(135deg, #eab308, #f97316)' }, // yellow-orange
    ]

    const gradientStyle = gradientColors[index % gradientColors.length]

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString('en-GB', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        })
    }

    return (
        <div className="space-y-3">
            {/* Rounded wrapper for preview only (not captured in download) */}
            <div className="rounded-xl shadow-lg overflow-hidden">
                {/* Instagram-sized card (400x400 preview) - no rounded corners for download */}
                <div
                    ref={cardRef}
                    style={{
                        width: '400px',
                        height: '400px',
                        fontFamily: "'Poppins', sans-serif",
                        position: 'relative',
                        ...gradientStyle
                    }}
                >
                    {/* Background image if available - use proxied base64 for download compatibility */}
                    {proxyImageUrl && (
                        <img
                            src={proxyImageUrl}
                            alt=""
                            style={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                width: '100%',
                                height: '100%',
                                objectFit: 'cover',
                                zIndex: 0
                            }}
                        />
                    )}

                    {/* Dark overlay for images */}
                    {proxyImageUrl && (
                        <div
                            style={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                right: 0,
                                bottom: 0,
                                background: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.7) 100%)',
                                zIndex: 1
                            }}
                        />
                    )}

                    {/* Content */}
                    <div
                        style={{
                            position: 'relative',
                            zIndex: 2,
                            height: '100%',
                            display: 'flex',
                            flexDirection: 'column',
                            padding: '24px',
                            color: '#ffffff'
                        }}
                    >
                        {/* Header with emoji */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                            <span style={{ fontSize: '30px' }}>✊</span>
                            <span style={{ fontSize: '18px', fontWeight: 600, color: 'rgba(255,255,255,0.9)' }}>Union Win</span>
                        </div>

                        {/* Main title */}
                        <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
                            <h3
                                style={{
                                    fontWeight: 700,
                                    lineHeight: 1.2,
                                    fontSize: win.title.length > 80 ? '20px' : win.title.length > 50 ? '24px' : '28px',
                                    textShadow: '0 2px 4px rgba(0,0,0,0.3)',
                                    margin: 0
                                }}
                            >
                                {win.title}
                            </h3>
                        </div>

                        {/* Footer info */}
                        <div style={{ marginTop: '16px' }}>
                            {/* Union name */}
                            <div
                                style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    padding: '6px 14px',
                                    borderRadius: '9999px',
                                    fontSize: '14px',
                                    fontWeight: 500,
                                    backgroundColor: 'rgba(255,255,255,0.25)',
                                    whiteSpace: 'nowrap'
                                }}
                            >
                                <span>🏛️</span>
                                <span>{win.union_name ?? 'Workers United'}</span>
                            </div>

                            {/* Date */}
                            <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.9)', textShadow: '0 1px 2px rgba(0,0,0,0.3)', marginTop: '10px' }}>
                                📅 {formatDate(win.date)}
                            </div>

                            {/* Branding */}
                            <div style={{ paddingTop: '12px', fontSize: '12px', fontWeight: 600, color: 'rgba(255,255,255,0.85)', textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}>
                                whathaveunionsdoneforus.uk
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Download button */}
            <button
                onClick={downloadAsImage}
                disabled={downloading}
                className="w-full bg-gray-700 text-white py-2 px-3 rounded-lg hover:bg-gray-800 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-2 text-sm"
                aria-label={`Download post for ${win.title}`}
            >
                {downloading ? (
                    <>
                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Generating...
                    </>
                ) : (
                    <>
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Download
                    </>
                )}
            </button>

            {/* Upload to Instagram button */}
            <button
                onClick={uploadToInstagram}
                disabled={uploading}
                className={`w-full py-2 px-3 rounded-lg transition-colors flex items-center justify-center gap-2 text-sm ${uploadStatus === 'success'
                    ? 'bg-green-600 text-white'
                    : uploadStatus === 'error'
                        ? 'bg-red-600 text-white hover:bg-red-700'
                        : 'bg-gradient-to-r from-purple-600 via-pink-600 to-orange-500 text-white hover:from-purple-700 hover:via-pink-700 hover:to-orange-600 disabled:opacity-50'
                    }`}
                aria-label={`Upload post for ${win.title} to Instagram`}
            >
                {uploading ? (
                    <>
                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Uploading...
                    </>
                ) : uploadStatus === 'success' ? (
                    <>
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Posted!
                    </>
                ) : uploadStatus === 'error' ? (
                    <>
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        Failed - Try Again
                    </>
                ) : (
                    <>
                        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                        </svg>
                        Upload to Instagram
                    </>
                )}
            </button>
        </div>
    )
}

function InfographicCard({ data, period }: InfographicCardProps) {
    const cardRef = useRef<HTMLDivElement>(null)
    const [downloading, setDownloading] = useState(false)

    // Load Google Font for the infographic
    useEffect(() => {
        const link = document.createElement('link')
        link.href = 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap'
        link.rel = 'stylesheet'
        document.head.appendChild(link)
        return () => {
            document.head.removeChild(link)
        }
    }, [])

    const downloadAsImage = useCallback(async () => {
        if (!cardRef.current) return

        setDownloading(true)
        try {
            const dataUrl = await toPng(cardRef.current, {
                quality: 1,
                pixelRatio: 2, // Higher resolution for social media
                backgroundColor: '#ffffff'
            })

            const link = document.createElement('a')
            link.download = `union-wins-${period}-${new Date().toISOString().split('T')[0]}.png`
            link.href = dataUrl
            link.click()
        } catch (error) {
            console.error('Failed to generate image:', error)
        } finally {
            setDownloading(false)
        }
    }, [period])

    const getGradientStyle = (period: TimePeriod): React.CSSProperties => {
        switch (period) {
            case 'week':
                return { background: 'linear-gradient(to right, #f97316, #dc2626)' }
            case 'month':
                return { background: 'linear-gradient(to right, #3b82f6, #9333ea)' }
            case 'year':
                return { background: 'linear-gradient(to right, #22c55e, #14b8a6)' }
        }
    }

    const getEmojiForPeriod = (period: TimePeriod): string => {
        switch (period) {
            case 'week':
                return '📅'
            case 'month':
                return '📆'
            case 'year':
                return '🎉'
        }
    }

    if (data.totalCount === 0) {
        return (
            <div className="bg-gray-100 rounded-lg p-6 text-center">
                <p className="text-gray-500">No wins recorded for {data.periodLabel.toLowerCase()}</p>
            </div>
        )
    }

    return (
        <div className="space-y-4">
            {/* The infographic card */}
            <div
                ref={cardRef}
                data-infographic-card
                className="rounded-xl shadow-lg overflow-hidden"
                style={{
                    width: '600px',
                    minHeight: '400px',
                    backgroundColor: '#ffffff',
                    fontFamily: "'Poppins', sans-serif"
                }}
            >
                {/* Header */}
                <div className="p-6" style={{ ...getGradientStyle(period), color: '#ffffff' }}>
                    <div className="flex items-center gap-3 mb-2">
                        <span className="text-4xl">{getEmojiForPeriod(period)}</span>
                        <div>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Union Wins {data.periodLabel}</h3>
                            <p className="text-sm" style={{ color: 'rgba(255,255,255,0.8)' }}>{data.periodDates}</p>
                        </div>
                    </div>
                    <div className="mt-4 text-center">
                        <div style={{ fontSize: '4rem', fontWeight: 800, lineHeight: 1 }}>{data.totalCount}</div>
                        <div style={{ fontSize: '1.25rem', color: 'rgba(255,255,255,0.9)', fontWeight: 600 }}>
                            {data.totalCount === 1 ? 'Victory' : 'Victories'} for Workers
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Stats Row */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="rounded-lg p-4 text-center" style={{ backgroundColor: '#f9fafb' }}>
                            <div className="text-3xl font-bold" style={{ color: '#1f2937' }}>{data.avgPerWeek}</div>
                            <div className="text-sm" style={{ color: '#4b5563' }}>Wins per Week</div>
                        </div>
                        <div className="rounded-lg p-4 text-center" style={{ backgroundColor: '#f9fafb' }}>
                            <div className="text-3xl font-bold" style={{ color: '#1f2937' }}>{data.uniqueUnions}</div>
                            <div className="text-sm" style={{ color: '#4b5563' }}>Active Unions</div>
                        </div>
                        <div className="rounded-lg p-4 text-center" style={{ backgroundColor: '#f9fafb' }}>
                            <div className="text-3xl font-bold" style={{ color: '#1f2937' }}>{data.allWinTypes.length}</div>
                            <div className="text-sm" style={{ color: '#4b5563' }}>Win Categories</div>
                        </div>
                    </div>

                    {/* Win Types Donut Chart */}
                    {data.allWinTypes.length > 0 && (
                        <div>
                            <h4 className="text-lg font-semibold mb-3 flex items-center gap-2" style={{ color: '#1f2937' }}>
                                <span>📊</span> Win Distribution
                            </h4>
                            <div className="flex items-center gap-6">
                                {/* Donut Chart */}
                                <div className="relative w-32 h-32 flex-shrink-0">
                                    <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                                        {(() => {
                                            const total = data.allWinTypes.reduce((sum, wt) => sum + wt.count, 0)
                                            let currentAngle = 0
                                            const colors = ['#ea580c', '#2563eb', '#16a34a', '#9333ea', '#eab308', '#06b6d4', '#ec4899']
                                            const outerRadius = 40
                                            const innerRadius = 25

                                            return data.allWinTypes.slice(0, 6).map((winType, index) => {
                                                const percentage = winType.count / total
                                                const angle = percentage * 360
                                                const startAngle = currentAngle
                                                const endAngle = currentAngle + angle
                                                currentAngle = endAngle

                                                const startRad = (startAngle * Math.PI) / 180
                                                const endRad = (endAngle * Math.PI) / 180

                                                // Outer arc points
                                                const x1 = 50 + outerRadius * Math.cos(startRad)
                                                const y1 = 50 + outerRadius * Math.sin(startRad)
                                                const x2 = 50 + outerRadius * Math.cos(endRad)
                                                const y2 = 50 + outerRadius * Math.sin(endRad)

                                                // Inner arc points
                                                const x3 = 50 + innerRadius * Math.cos(endRad)
                                                const y3 = 50 + innerRadius * Math.sin(endRad)
                                                const x4 = 50 + innerRadius * Math.cos(startRad)
                                                const y4 = 50 + innerRadius * Math.sin(startRad)

                                                const largeArcFlag = angle > 180 ? 1 : 0

                                                return (
                                                    <path
                                                        key={winType.type}
                                                        d={`M ${x1} ${y1} A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x4} ${y4} Z`}
                                                        fill={colors[index % colors.length]}
                                                    />
                                                )
                                            })
                                        })()}
                                    </svg>
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <span className="text-2xl">✊</span>
                                    </div>
                                </div>
                                {/* Legend */}
                                <div className="flex-1 grid grid-cols-2 gap-2">
                                    {data.allWinTypes.slice(0, 6).map((winType, index) => {
                                        const hexColors = ['#ea580c', '#2563eb', '#16a34a', '#9333ea', '#eab308', '#06b6d4']
                                        return (
                                            <div key={winType.type} className="flex items-center gap-2">
                                                <div
                                                    className="w-3 h-3 rounded-full"
                                                    style={{ backgroundColor: hexColors[index % hexColors.length] }}
                                                />
                                                <span className="text-sm truncate" style={{ color: '#374151' }}>{winType.type}</span>
                                                <span className="text-sm font-semibold" style={{ color: '#6b7280' }}>({winType.count})</span>
                                            </div>
                                        )
                                    })}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Top Unions */}
                    {data.topUnions.length > 0 && (
                        <div>
                            <h4 className="text-lg font-semibold mb-3 flex items-center gap-2" style={{ color: '#1f2937' }}>
                                <span>🏆</span> Most Active Unions
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {data.topUnions.map((union, index) => (
                                    <span
                                        key={union.name}
                                        className="px-3 py-1 rounded-full text-sm font-medium"
                                        style={
                                            index === 0
                                                ? { ...getGradientStyle(period), color: '#ffffff' }
                                                : { backgroundColor: '#f3f4f6', color: '#374151' }
                                        }
                                    >
                                        {index === 0 && '🥇 '}{union.name} ({union.count})
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Recent Pay Rises */}
                    {data.recentPayRises.length > 0 && (
                        <div>
                            <h4 className="text-lg font-semibold mb-3 flex items-center gap-2" style={{ color: '#1f2937' }}>
                                <span>💰</span> Recent Pay Rises
                            </h4>
                            <div className="space-y-2">
                                {data.recentPayRises.map((win) => (
                                    <div
                                        key={win.id}
                                        className="rounded-lg p-3"
                                        style={{ backgroundColor: '#fef3c7' }}
                                    >
                                        <div className="font-semibold text-sm" style={{ color: '#78350f' }}>
                                            {win.title}
                                        </div>
                                        <div className="text-xs" style={{ color: '#92400e' }}>
                                            {win.union_name ?? 'Union'}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Footer branding */}
                    <div className="pt-4 text-center" style={{ borderTop: '1px solid #e5e7eb' }}>
                        <p className="text-sm" style={{ color: '#6b7280' }}>
                            Find out more at <span style={{ color: '#2563eb' }}>whathaveunionsdoneforus.uk</span>
                        </p>
                    </div>
                </div>
            </div>

            {/* Download button */}
            <button
                onClick={downloadAsImage}
                disabled={downloading}
                className="w-full bg-gray-800 text-white py-3 px-4 rounded-lg hover:bg-gray-900 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-2"
                aria-label={`Download ${data.periodLabel} infographic as image`}
            >
                {downloading ? (
                    <>
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">
                            <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                                fill="none"
                            />
                            <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                        </svg>
                        Generating...
                    </>
                ) : (
                    <>
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Download for Social Media
                    </>
                )}
            </button>
        </div>
    )
}

export function AdminInfographics({ adminPassword }: AdminInfographicsProps) {
    const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>('week')
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [recentWins, setRecentWins] = useState<UnionWin[]>([])
    const [infographicData, setInfographicData] = useState<Record<TimePeriod, InfographicData | null>>({
        week: null,
        month: null,
        year: null
    })

    useEffect(() => {
        const filterWinsByPeriod = (allWins: UnionWin[], period: TimePeriod): UnionWin[] => {
            const { start, end } = getDateRange(period)
            return allWins.filter(win => {
                const winDate = new Date(win.date)
                return winDate >= start && winDate <= end
            })
        }

        const fetchAllWins = async () => {
            setLoading(true)
            setError(null)

            try {
                // Fetch all wins once and filter by occurred date client-side
                const response = await fetch('/api/wins', {
                    headers: {
                        'X-Admin-Password': adminPassword
                    }
                })

                if (!response.ok) {
                    throw new Error('Failed to fetch wins')
                }

                const allWins: UnionWin[] = await response.json()

                // Get 5 most recent wins for post cards
                const sortedWins = [...allWins].sort((a, b) =>
                    new Date(b.date).getTime() - new Date(a.date).getTime()
                )
                setRecentWins(sortedWins.slice(0, 10))

                // Filter wins by their occurred date for each period
                const weekWins = filterWinsByPeriod(allWins, 'week')
                const monthWins = filterWinsByPeriod(allWins, 'month')
                const yearWins = filterWinsByPeriod(allWins, 'year')

                setInfographicData({
                    week: aggregateWinData(weekWins, 'week'),
                    month: aggregateWinData(monthWins, 'month'),
                    year: aggregateWinData(yearWins, 'year')
                })
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load data')
            } finally {
                setLoading(false)
            }
        }

        fetchAllWins()
    }, [adminPassword])

    const periods: { id: TimePeriod; label: string; icon: string }[] = [
        { id: 'week', label: 'This Week', icon: '📅' },
        { id: 'month', label: 'This Month', icon: '📆' },
        { id: 'year', label: 'This Year', icon: '🎉' }
    ]

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600" role="status">
                    <span className="sr-only">Loading...</span>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4" role="alert">
                <p className="text-red-800">{error}</p>
            </div>
        )
    }

    return (
        <div className="space-y-8">
            {/* Recent Posts Section */}
            <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">📱 Recent Posts</h2>
                <p className="text-gray-600 mb-4">
                    Instagram-ready cards for the 10 most recent union wins. Click to download.
                </p>
                <div className="flex gap-6 overflow-x-auto pb-4">
                    {recentWins.map((win, index) => (
                        <PostCard key={win.id} win={win} index={index} />
                    ))}
                </div>
            </div>

            <hr className="border-gray-200" />

            {/* Period Infographics Section */}
            <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">📊 Period Summaries</h2>
                <p className="text-gray-600">
                    Generate shareable infographics summarizing union wins for different time periods.
                </p>
            </div>

            {/* Period selector */}
            <div className="flex gap-2" role="tablist" aria-label="Time period selection">
                {periods.map(period => (
                    <button
                        key={period.id}
                        onClick={() => setSelectedPeriod(period.id)}
                        role="tab"
                        aria-selected={selectedPeriod === period.id}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${selectedPeriod === period.id
                            ? 'bg-orange-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        <span>{period.icon}</span>
                        {period.label}
                    </button>
                ))}
            </div>

            {/* Infographic display */}
            <div className="flex justify-center">
                {infographicData[selectedPeriod] && (
                    <InfographicCard
                        data={infographicData[selectedPeriod]!}
                        period={selectedPeriod}
                    />
                )}
            </div>
        </div>
    )
}
