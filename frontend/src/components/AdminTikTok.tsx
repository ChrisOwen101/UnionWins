import { useState } from 'react'

interface AdminTikTokProps {
    adminPassword: string
}

interface TikTokResult {
    success: boolean
    win_id?: number
    win_title?: string
    script?: string
    caption?: string
    video_filename?: string
    temp_path?: string
    message?: string
}

export const AdminTikTok: React.FC<AdminTikTokProps> = ({ adminPassword }) => {
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<TikTokResult | null>(null)
    const [error, setError] = useState<string | null>(null)

    const handleCreateVideo = async () => {
        setLoading(true)
        setError(null)
        setResult(null)

        try {
            const response = await fetch('/api/admin/tiktok/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Admin-Password': adminPassword,
                },
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Failed to create TikTok video')
            }

            const data = await response.json()
            setResult(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
        } finally {
            setLoading(false)
        }
    }

    const handleDownload = async () => {
        if (!result?.temp_path) return

        try {
            const response = await fetch(
                `/api/admin/tiktok/download?video_path=${encodeURIComponent(result.temp_path)}`,
                {
                    headers: {
                        'X-Admin-Password': adminPassword,
                    },
                }
            )

            if (!response.ok) {
                throw new Error('Failed to download video')
            }

            const blob = await response.blob()
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = result.video_filename || 'union_win_video.mp4'
            document.body.appendChild(a)
            a.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to download video')
        }
    }

    return (
        <div className="space-y-6">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    Create TikTok Video
                </h2>
                <p className="text-gray-600 mb-6">
                    Generate a TikTok video for the most recent union win. The video will include:
                </p>
                <ul className="list-disc list-inside text-gray-600 mb-6 space-y-1">
                    <li>Blue background in vertical format (9:16)</li>
                    <li>Win title and union name</li>
                    <li>AI-generated voiceover script</li>
                    <li>UnionWins.com branding</li>
                </ul>

                <button
                    onClick={handleCreateVideo}
                    disabled={loading}
                    className={`px-6 py-3 rounded-lg font-medium transition-colors ${loading
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-orange-600 text-white hover:bg-orange-700'
                        }`}
                >
                    {loading ? (
                        <>
                            <span className="inline-block animate-spin mr-2">⏳</span>
                            Creating Video...
                        </>
                    ) : (
                        '🎬 Create TikTok Video'
                    )}
                </button>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h3 className="text-red-800 font-semibold mb-2">Error</h3>
                    <p className="text-red-700">{error}</p>
                </div>
            )}

            {result && result.success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6 space-y-4">
                    <h3 className="text-green-800 font-semibold text-lg">
                        ✅ Video Created Successfully!
                    </h3>

                    <div className="space-y-3">
                        <div>
                            <h4 className="font-semibold text-gray-900 mb-1">Win Title:</h4>
                            <p className="text-gray-700">{result.win_title}</p>
                        </div>

                        {result.script && (
                            <div>
                                <h4 className="font-semibold text-gray-900 mb-1">Script:</h4>
                                <p className="text-gray-700 bg-white p-3 rounded border border-gray-200">
                                    {result.script}
                                </p>
                            </div>
                        )}

                        {result.caption && (
                            <div>
                                <h4 className="font-semibold text-gray-900 mb-1">
                                    Suggested Caption:
                                </h4>
                                <p className="text-gray-700 bg-white p-3 rounded border border-gray-200 whitespace-pre-wrap">
                                    {result.caption}
                                </p>
                            </div>
                        )}

                        <div className="pt-4">
                            <button
                                onClick={handleDownload}
                                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                            >
                                📥 Download Video ({result.video_filename})
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-blue-800 font-semibold mb-2">ℹ️ How it works</h3>
                <ol className="list-decimal list-inside text-blue-700 space-y-1">
                    <li>Fetches the most recent approved union win</li>
                    <li>Generates an engaging 20-second script using AI</li>
                    <li>Converts the script to speech with a friendly voice</li>
                    <li>Creates a vertical video (1080x1920) with branding</li>
                    <li>Returns the video file for download</li>
                </ol>
                <p className="text-blue-700 mt-3">
                    <strong>Note:</strong> Video creation may take 30-60 seconds depending on the
                    script length and server load.
                </p>
            </div>
        </div>
    )
}
