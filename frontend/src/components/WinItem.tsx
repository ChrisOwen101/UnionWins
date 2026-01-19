import { useState, useEffect } from 'react'
import type { UnionWin, MousePosition } from '../types'
import { WinTooltip } from './WinTooltip'
import { WinMetadata } from './WinMetadata'
import { isDesktop } from '../utils/deviceDetection'

interface WinItemProps {
    win: UnionWin
}

/**
 * Individual win item component
 */
export const WinItem: React.FC<WinItemProps> = ({ win }) => {
    const [isHovered, setIsHovered] = useState(false)
    const [mousePosition, setMousePosition] = useState<MousePosition>({ x: 0, y: 0 })
    const [isDesktopDevice, setIsDesktopDevice] = useState(false)

    useEffect(() => {
        setIsDesktopDevice(isDesktop())
    }, [])

    const handleMouseMove = (e: React.MouseEvent) => {
        setMousePosition({ x: e.clientX, y: e.clientY })
    }

    return (
        <li className="flex gap-4 relative">
            {isHovered && isDesktopDevice && <WinTooltip win={win} position={mousePosition} />}

            {win.emoji && (
                <div className="text-2xl pt-0.5" aria-hidden="true">
                    {win.emoji}
                </div>
            )}

            <div className="flex-1 min-w-0">
                <h2 className="text-base leading-snug">
                    <a
                        href={win.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-900 hover:text-gray-600"
                        onMouseEnter={() => setIsHovered(true)}
                        onMouseLeave={() => setIsHovered(false)}
                        onMouseMove={handleMouseMove}
                    >
                        {win.title}
                    </a>
                </h2>
                <WinMetadata
                    unionName={win.union_name}
                    url={win.url}
                    date={win.date}
                />
            </div>
        </li >
    )
}
