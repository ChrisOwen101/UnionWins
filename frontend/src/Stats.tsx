import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    LineChart,
    Line,
    Legend,
} from 'recharts'
import type { UnionWin } from './types'

// Color palette for charts
const COLORS = [
    '#f97316', // orange-500
    '#3b82f6', // blue-500
    '#10b981', // emerald-500
    '#8b5cf6', // violet-500
    '#ec4899', // pink-500
    '#06b6d4', // cyan-500
    '#f59e0b', // amber-500
    '#6366f1', // indigo-500
    '#14b8a6', // teal-500
    '#ef4444', // red-500
    '#84cc16', // lime-500
]

interface StatsData {
    unionCounts: { name: string; count: number }[]
    typeCounts: { name: string; count: number }[]
    monthlyTrends: { month: string; count: number }[]
    yearlyTrends: { year: string; count: number }[]
    topUnionsByType: Record<string, { name: string; count: number }[]>
    totalWins: number
    uniqueUnions: number
    dateRange: { earliest: string; latest: string }
}

/**
 * Stats page displaying various charts and analytics about union wins.
 * Designed to be useful for TUC (Trades Union Congress) workers.
 */
function Stats() {
    const [wins, setWins] = useState<UnionWin[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<Error | null>(null)

    // Fetch all wins for statistics
    useEffect(() => {
        const fetchAllWins = async () => {
            try {
                setLoading(true)
                const response = await fetch('/api/wins')
                if (!response.ok) {
                    throw new Error('Failed to fetch wins')
                }
                const data: UnionWin[] = await response.json()
                setWins(data)
            } catch (err) {
                console.error('Error fetching wins:', err)
                setError(err as Error)
            } finally {
                setLoading(false)
            }
        }

        fetchAllWins()
    }, [])

    // Calculate statistics from wins data
    const stats: StatsData = useMemo(() => {
        if (wins.length === 0) {
            return {
                unionCounts: [],
                typeCounts: [],
                monthlyTrends: [],
                yearlyTrends: [],
                topUnionsByType: {},
                totalWins: 0,
                uniqueUnions: 0,
                dateRange: { earliest: '', latest: '' },
            }
        }

        // Helper to parse comma-separated win_types
        const parseWinTypes = (winTypes?: string): string[] => {
            if (!winTypes) return ['Other']
            const types = winTypes.split(',').map(t => t.trim()).filter(Boolean)
            return types.length > 0 ? types : ['Other']
        }

        // Count wins by union
        const unionMap = new Map<string, number>()
        wins.forEach(win => {
            const union = win.union_name || 'Unknown'
            unionMap.set(union, (unionMap.get(union) || 0) + 1)
        })
        const unionCounts = Array.from(unionMap.entries())
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 15) // Top 15 unions

        // Count wins by type (each win can have multiple types)
        const typeMap = new Map<string, number>()
        wins.forEach(win => {
            const types = parseWinTypes(win.win_types)
            types.forEach(type => {
                typeMap.set(type, (typeMap.get(type) || 0) + 1)
            })
        })
        const typeCounts = Array.from(typeMap.entries())
            .map(([name, count]) => ({ name, count }))
            .sort((a, b) => b.count - a.count)

        // Monthly trends (last 12 months)
        const monthMap = new Map<string, number>()
        wins.forEach(win => {
            const date = new Date(win.date)
            const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
            monthMap.set(monthKey, (monthMap.get(monthKey) || 0) + 1)
        })
        const sortedMonths = Array.from(monthMap.keys()).sort()
        const monthlyTrends = sortedMonths.slice(-12).map(month => ({
            month: formatMonth(month),
            count: monthMap.get(month) || 0,
        }))

        // Yearly trends
        const yearMap = new Map<string, number>()
        wins.forEach(win => {
            const year = new Date(win.date).getFullYear().toString()
            yearMap.set(year, (yearMap.get(year) || 0) + 1)
        })
        const yearlyTrends = Array.from(yearMap.entries())
            .map(([year, count]) => ({ year, count }))
            .sort((a, b) => a.year.localeCompare(b.year))

        // Top unions by win type
        const topUnionsByType: Record<string, { name: string; count: number }[]> = {}
        const typeUnionMap = new Map<string, Map<string, number>>()
        wins.forEach(win => {
            const types = parseWinTypes(win.win_types)
            const union = win.union_name || 'Unknown'
            types.forEach(type => {
                if (!typeUnionMap.has(type)) {
                    typeUnionMap.set(type, new Map())
                }
                const unionMapForType = typeUnionMap.get(type)!
                unionMapForType.set(union, (unionMapForType.get(union) || 0) + 1)
            })
        })
        typeUnionMap.forEach((unionMapForType, type) => {
            topUnionsByType[type] = Array.from(unionMapForType.entries())
                .map(([name, count]) => ({ name, count }))
                .sort((a, b) => b.count - a.count)
                .slice(0, 5)
        })

        // Date range
        const dates = wins.map(w => new Date(w.date).getTime())
        const earliest = new Date(Math.min(...dates)).toLocaleDateString('en-GB', {
            month: 'long',
            year: 'numeric',
        })
        const latest = new Date(Math.max(...dates)).toLocaleDateString('en-GB', {
            month: 'long',
            year: 'numeric',
        })

        // Unique unions
        const uniqueUnions = new Set(wins.map(w => w.union_name).filter(Boolean)).size

        return {
            unionCounts,
            typeCounts,
            monthlyTrends,
            yearlyTrends,
            topUnionsByType,
            totalWins: wins.length,
            uniqueUnions,
            dateRange: { earliest, latest },
        }
    }, [wins])

    if (loading) {
        return (
            <div className="min-h-screen bg-neutral-50">
                <StatsHeader />
                <main className="max-w-6xl mx-auto px-5 py-6">
                    <div className="flex justify-center items-center py-20">
                        <div className="animate-pulse text-gray-500">Loading statistics...</div>
                    </div>
                </main>
            </div>
        )
    }

    if (error) {
        return (
            <div className="min-h-screen bg-neutral-50">
                <StatsHeader />
                <main className="max-w-6xl mx-auto px-5 py-6">
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                        Error loading statistics: {error.message}
                    </div>
                </main>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-neutral-50">
            <StatsHeader />

            <main id="main-content" className="max-w-6xl mx-auto px-5 py-6" tabIndex={-1}>
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <SummaryCard
                        title="Total Wins"
                        value={stats.totalWins.toLocaleString()}
                        icon="🏆"
                    />
                    <SummaryCard
                        title="Unique Unions"
                        value={stats.uniqueUnions.toLocaleString()}
                        icon="🤝"
                    />
                    <SummaryCard
                        title="Win Types"
                        value={stats.typeCounts.length.toString()}
                        icon="📊"
                    />
                    <SummaryCard
                        title="Data Range"
                        value={`${stats.dateRange.earliest} - ${stats.dateRange.latest}`}
                        icon="📅"
                        small
                    />
                </div>

                {/* Monthly Activity Trend */}
                <ChartCard title="Monthly Win Activity (Last 12 Months)" subtitle="Track how union wins are trending over time">
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={stats.monthlyTrends}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis
                                dataKey="month"
                                tick={{ fontSize: 12 }}
                                tickLine={false}
                                axisLine={{ stroke: '#e5e7eb' }}
                            />
                            <YAxis
                                tick={{ fontSize: 12 }}
                                tickLine={false}
                                axisLine={{ stroke: '#e5e7eb' }}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'white',
                                    border: '1px solid #e5e7eb',
                                    borderRadius: '8px',
                                }}
                            />
                            <Line
                                type="monotone"
                                dataKey="count"
                                stroke="#f97316"
                                strokeWidth={2}
                                dot={{ fill: '#f97316', strokeWidth: 2, r: 4 }}
                                activeDot={{ r: 6, fill: '#f97316' }}
                                name="Wins"
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </ChartCard>

                {/* Two column layout for pie and bar */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    {/* Win Types Distribution */}
                    <ChartCard title="Wins by Type" subtitle="Distribution of win categories">
                        <ResponsiveContainer width="100%" height={350}>
                            <PieChart>
                                <Pie
                                    data={stats.typeCounts}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={2}
                                    dataKey="count"
                                    nameKey="name"
                                    label={({ name, percent }) =>
                                        `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`
                                    }
                                    labelLine={{ stroke: '#9ca3af', strokeWidth: 1 }}
                                >
                                    {stats.typeCounts.map((_, index) => (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={COLORS[index % COLORS.length]}
                                        />
                                    ))}
                                </Pie>
                                <Tooltip
                                    formatter={(value) => [value, 'Wins']}
                                    contentStyle={{
                                        backgroundColor: 'white',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '8px',
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </ChartCard>

                    {/* Yearly Trends */}
                    <ChartCard title="Wins by Year" subtitle="Year-over-year comparison">
                        <ResponsiveContainer width="100%" height={350}>
                            <BarChart data={stats.yearlyTrends}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                                <XAxis
                                    dataKey="year"
                                    tick={{ fontSize: 12 }}
                                    tickLine={false}
                                    axisLine={{ stroke: '#e5e7eb' }}
                                />
                                <YAxis
                                    tick={{ fontSize: 12 }}
                                    tickLine={false}
                                    axisLine={{ stroke: '#e5e7eb' }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'white',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '8px',
                                    }}
                                />
                                <Bar
                                    dataKey="count"
                                    fill="#3b82f6"
                                    radius={[4, 4, 0, 0]}
                                    name="Wins"
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </ChartCard>
                </div>

                {/* Top Unions Bar Chart */}
                <ChartCard
                    title="Top 15 Unions by Number of Wins"
                    subtitle="Which unions are achieving the most recorded victories"
                >
                    <ResponsiveContainer width="100%" height={500}>
                        <BarChart
                            data={stats.unionCounts}
                            layout="vertical"
                            margin={{ left: 20, right: 20 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal />
                            <XAxis type="number" tick={{ fontSize: 12 }} tickLine={false} />
                            <YAxis
                                type="category"
                                dataKey="name"
                                tick={{ fontSize: 11 }}
                                tickLine={false}
                                width={150}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'white',
                                    border: '1px solid #e5e7eb',
                                    borderRadius: '8px',
                                }}
                            />
                            <Bar dataKey="count" fill="#f97316" radius={[0, 4, 4, 0]} name="Wins" />
                        </BarChart>
                    </ResponsiveContainer>
                </ChartCard>

                {/* Win Types Breakdown by Union */}
                <ChartCard
                    title="Top Performing Unions by Win Type"
                    subtitle="See which unions excel in each category of wins"
                >
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {Object.entries(stats.topUnionsByType)
                            .filter(([, unions]) => unions.length > 0)
                            .sort(([a], [b]) => a.localeCompare(b))
                            .map(([type, unions]) => (
                                <div
                                    key={type}
                                    className="bg-gray-50 rounded-lg p-4 border border-gray-100"
                                >
                                    <h4 className="font-semibold text-gray-900 mb-3 text-sm">
                                        {type}
                                    </h4>
                                    <ul className="space-y-2">
                                        {unions.map((union, index) => (
                                            <li
                                                key={union.name}
                                                className="flex justify-between items-center text-sm"
                                            >
                                                <span className="text-gray-700 truncate mr-2">
                                                    {index + 1}. {union.name}
                                                </span>
                                                <span className="text-gray-500 font-medium">
                                                    {union.count}
                                                </span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                    </div>
                </ChartCard>

                {/* Win Types Comparison - Stacked Bar by Year */}
                <ChartCard
                    title="Win Types Over Time"
                    subtitle="How different types of wins have evolved year by year"
                >
                    <WinTypesByYearChart wins={wins} />
                </ChartCard>
            </main>
        </div>
    )
}

/**
 * Header component for the Stats page
 */
function StatsHeader() {
    return (
        <header className="bg-white border-b border-gray-200 px-5 py-4">
            <div className="max-w-6xl mx-auto flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-light text-gray-900">Union Wins Statistics</h1>
                    <p className="text-gray-600 mt-1">Insights and trends from recorded union victories</p>
                </div>
                <nav aria-label="Stats navigation" className="flex items-center gap-4">
                    <Link
                        to="/"
                        className="text-gray-600 hover:text-gray-800 transition-colors text-sm font-medium px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
                    >
                        ← Back to Wins
                    </Link>
                </nav>
            </div>
        </header>
    )
}

/**
 * Summary card component for key metrics
 */
interface SummaryCardProps {
    title: string
    value: string
    icon: string
    small?: boolean
}

function SummaryCard({ title, value, icon, small }: SummaryCardProps) {
    return (
        <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-gray-500 text-sm mb-1">{title}</p>
                    <p className={`font-semibold text-gray-900 ${small ? 'text-sm' : 'text-2xl'}`}>
                        {value}
                    </p>
                </div>
                <span className="text-3xl" role="img" aria-hidden="true">
                    {icon}
                </span>
            </div>
        </div>
    )
}

/**
 * Card wrapper for charts
 */
interface ChartCardProps {
    title: string
    subtitle?: string
    children: React.ReactNode
}

function ChartCard({ title, subtitle, children }: ChartCardProps) {
    return (
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm mb-6">
            <div className="mb-4">
                <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
                {subtitle && <p className="text-gray-500 text-sm mt-1">{subtitle}</p>}
            </div>
            {children}
        </div>
    )
}

/**
 * Chart showing win types distribution over years
 */
function WinTypesByYearChart({ wins }: { wins: UnionWin[] }) {
    const data = useMemo(() => {
        const yearTypeMap = new Map<string, Record<string, number>>()

        // Helper to parse comma-separated win_types
        const parseWinTypes = (winTypes?: string): string[] => {
            if (!winTypes) return ['Other']
            const types = winTypes.split(',').map(t => t.trim()).filter(Boolean)
            return types.length > 0 ? types : ['Other']
        }

        wins.forEach(win => {
            const year = new Date(win.date).getFullYear().toString()
            const types = parseWinTypes(win.win_types)

            if (!yearTypeMap.has(year)) {
                yearTypeMap.set(year, {})
            }
            const typeMap = yearTypeMap.get(year)!
            types.forEach(type => {
                typeMap[type] = (typeMap[type] || 0) + 1
            })
        })

        // Convert to chart data
        return Array.from(yearTypeMap.entries())
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([year, types]) => ({
                year,
                ...types,
            }))
    }, [wins])

    // Get unique types for the legend
    const types = useMemo(() => {
        const allTypes = new Set<string>()
        wins.forEach(win => {
            if (win.win_types) {
                win.win_types.split(',').map(t => t.trim()).filter(Boolean).forEach(t => allTypes.add(t))
            } else {
                allTypes.add('Other')
            }
        })
        return Array.from(allTypes).sort()
    }, [wins])

    if (data.length === 0) {
        return <p className="text-gray-500">No data available</p>
    }

    return (
        <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                    dataKey="year"
                    tick={{ fontSize: 12 }}
                    tickLine={false}
                    axisLine={{ stroke: '#e5e7eb' }}
                />
                <YAxis tick={{ fontSize: 12 }} tickLine={false} axisLine={{ stroke: '#e5e7eb' }} />
                <Tooltip
                    contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                    }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                {types.map((type, index) => (
                    <Bar
                        key={type}
                        dataKey={type}
                        stackId="a"
                        fill={COLORS[index % COLORS.length]}
                    />
                ))}
            </BarChart>
        </ResponsiveContainer>
    )
}

/**
 * Format month string (YYYY-MM) to readable format
 */
function formatMonth(monthKey: string): string {
    const [year, month] = monthKey.split('-')
    const date = new Date(parseInt(year), parseInt(month) - 1)
    return date.toLocaleDateString('en-GB', { month: 'short', year: '2-digit' })
}

export default Stats
