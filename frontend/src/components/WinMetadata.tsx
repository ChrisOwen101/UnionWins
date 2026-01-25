import { getDomain } from '../utils/urlHelpers'
import { formatDate } from '../utils/dateFormatters'

interface WinMetadataProps {
    unionName?: string
    winTypes?: string // Comma-separated list of win types
    url: string
    date: string
}

/**
 * Parse comma-separated win types into an array
 */
const parseWinTypes = (winTypes?: string): string[] => {
    if (!winTypes) return []
    return winTypes.split(',').map(t => t.trim()).filter(Boolean)
}

/**
 * Display metadata for a win (union name, win types, domain, date)
 */
export const WinMetadata: React.FC<WinMetadataProps> = ({
    unionName,
    winTypes,
    url,
    date
}) => {
    const domain = getDomain(url)
    const formattedDate = formatDate(date)
    const typesList = parseWinTypes(winTypes)

    return (
        <div className="mt-1 text-xs text-gray-500 flex items-center gap-1.5 flex-wrap">
            {unionName && (
                <>
                    <span className="font-medium">{unionName}</span>
                    <span aria-hidden="true">·</span>
                </>
            )}
            {typesList.map((type, index) => (
                <span key={type}>
                    <span className="bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded text-[10px] font-medium">
                        {type}
                    </span>
                    {index < typesList.length - 1 && <span className="ml-1"> </span>}
                </span>
            ))}
            {typesList.length > 0 && (
                <span aria-hidden="true">·</span>
            )}
            <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-orange-600 hover:underline focus:outline-none focus:ring-2 focus:ring-orange-500 rounded"
                title={`Open article from ${domain}`}
            >
                {domain}
            </a>
            <span aria-hidden="true">·</span>
            <time dateTime={date} title={formattedDate}>
                {formattedDate}
            </time>
        </div>
    )
}
