import { getDomain } from '../utils/urlHelpers'
import { formatDate } from '../utils/dateFormatters'

interface WinMetadataProps {
    unionName?: string
    url: string
    date: string
}

/**
 * Display metadata for a win (union name, domain, date)
 */
export const WinMetadata: React.FC<WinMetadataProps> = ({
    unionName,
    url,
    date
}) => {
    const domain = getDomain(url)
    const formattedDate = formatDate(date)

    return (
        <div className="mt-1 text-xs text-gray-500 flex items-center gap-1.5 flex-wrap">
            {unionName && (
                <>
                    <span className="font-medium">{unionName}</span>
                    <span aria-hidden="true">·</span>
                </>
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
