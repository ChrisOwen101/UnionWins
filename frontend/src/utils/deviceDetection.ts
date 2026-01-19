/**
 * Detects if the device is desktop
 */
export const isDesktop = (): boolean => {
    return window.matchMedia('(hover: hover) and (pointer: fine)').matches
}
