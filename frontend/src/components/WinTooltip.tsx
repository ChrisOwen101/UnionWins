import type { UnionWin, MousePosition } from '../types'
import { filterCitations } from '../utils/textFormatters'

interface WinTooltipProps {
    win: UnionWin
    position: MousePosition
}

/**
 * Tooltip component showing win details on hover
 */
export const WinTooltip: React.FC<WinTooltipProps> = ({ win, position }) => {
    const cleanSummary = filterCitations(win.summary)

    return (
        <div
            className="fixed bg-gray-900 text-white text-sm rounded-lg p-3 shadow-xl z-50 w-72 pointer-events-none before:content-[''] before:absolute before:-left-2 before:top-3 before:border-8 before:border-transparent before:border-r-gray-900"
            style={{
                left: `${position.x + 15}px`,
                top: `${position.y + 15}px`
            }}
        >
            <h3 className="font-medium text-base mb-2">{win.title}</h3>
            {win.union_name && (
                <p className="text-xs text-gray-300 mb-2">
                    <span className="font-medium">Union:</span> {win.union_name}
                </p>
            )}
            {cleanSummary && (
                <p className="text-xs text-gray-200 leading-relaxed">
                    {cleanSummary}
                </p>
            )}
        </div>
    )
}
