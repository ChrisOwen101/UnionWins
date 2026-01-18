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
                    <span>·</span>
                </>
            )}
            <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-orange-500 hover:underline"
            >
                {domain}
            </a>
            <span>·</span>
            <span>{formattedDate}</span>
        </div>
    )
}
