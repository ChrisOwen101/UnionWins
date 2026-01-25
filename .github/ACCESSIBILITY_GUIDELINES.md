# Frontend Accessibility Guidelines - Quick Reference

## Overview

The UnionWins frontend has been updated to meet WCAG 2.1 AA accessibility standards. Follow these guidelines when modifying or adding new components.

## Key Accessibility Patterns

### 1. Form Inputs

```tsx
<label htmlFor="input-id">Label <span aria-label="required">*</span></label>
<input
    id="input-id"
    type="email"  // Use appropriate type (email, password, search, url, etc)
    aria-required="true"
    aria-invalid={hasError}
    aria-describedby={hasError ? "error-id" : undefined}
/>
{hasError && (
    <div id="error-id" role="alert">
        Error message
    </div>
)}
```

### 2. Buttons with Icons

```tsx
<button
  onClick={handleClick}
  aria-label="Clear search" // Describe the action
  className="focus:outline-none focus:ring-2 focus:ring-orange-500"
>
  <svg aria-hidden="true">{/* icon content */}</svg>
</button>
```

### 3. Links

```tsx
<a
  href="/path"
  target="_blank"
  rel="noopener noreferrer"
  className="focus:outline-none focus:ring-2 focus:ring-orange-500"
  aria-label="Link text (opens in new window)"
>
  Link Text
</a>
```

### 4. Modal Dialogs

```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby={errorId}
>
  <h2 id="modal-title">Modal Title</h2>
  {/* Modal content */}
</div>;

// Include keyboard handling:
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === "Escape") {
    handleClose();
  }
};
```

### 5. Loading States

```tsx
<div role="status" aria-live="polite" aria-busy="true">
  <div className="animate-spin" aria-hidden="true" />
  <span className="sr-only">Loading...</span>
</div>
```

### 6. Dynamic Content Updates

```tsx
<div role="region" aria-labelledby="results-label" aria-live="polite">
  <p id="results-label" className="sr-only">
    {wins.length} results found
  </p>
  {/* Results list */}
</div>
```

### 7. Tabs

```tsx
<div role="tablist" aria-label="Navigation">
    {tabs.map(tab => (
        <button
            role="tab"
            aria-selected={isActive}
            aria-controls={`panel-${tab.id}`}
            tabIndex={isActive ? 0 : -1}
        >
            {tab.label}
        </button>
    ))}
</div>

<div role="tabpanel" id="panel-id">
    {/* Panel content */}
</div>
```

## Screen Reader Only Content

```tsx
<span className="sr-only">Screen reader only text</span>
```

## Common Focus Styles

```css
/* For orange-themed components */
focus:outline-none focus:ring-2 focus:ring-orange-500

/* For blue-themed components */
focus:outline-none focus:ring-2 focus:ring-blue-500

/* With offset */
focus:outline-none focus:ring-2 focus:ring-offset-2
```

## Semantic HTML Elements

Always use semantic HTML over `<div>` when possible:

- `<header>` - Header/top navigation
- `<nav>` - Navigation with `aria-label`
- `<main>` - Main content area (one per page)
- `<section>` - Grouped content sections
- `<article>` - Self-contained content
- `<footer>` - Footer content
- `<time>` - Dates and times with `dateTime` attribute
- `<label>` - Form labels (always associate with input)
- `<fieldset>` - Grouped form inputs
- `<legend>` - Fieldset title
- `<button>` - Interactive elements (not divs)
- `<a>` - Links (not buttons)

## Decorative Elements

Mark decorative elements as hidden from screen readers:

```tsx
<span aria-hidden="true">•</span>  {/* Decorative separator */}
<svg aria-hidden="true">...</svg>  {/* Icon-only graphics */}
<img alt="" />  {/* Purely decorative images */}
```

## Heading Hierarchy

Maintain proper heading order:

```tsx
<h1>Page Title</h1>           {/* One per page */}
<h2>Section Title</h2>         {/* Main sections */}
<h3>Subsection Title</h3>      {/* Content subsections */}
<h4>Details Title</h4>         {/* Minor subsections */}
```

## Lists

Use semantic list elements:

```tsx
<ol>  {/* Ordered list */}
    <li>Item 1</li>
    <li>Item 2</li>
</ol>

<ul>  {/* Unordered list */}
    <li>Item 1</li>
    <li>Item 2</li>
</ul>
```

## Focus Management

Always manage focus in modals and special interactions:

```tsx
const previousFocusRef = useRef<HTMLElement | null>(null);

useEffect(() => {
  if (isOpen) {
    previousFocusRef.current = document.activeElement as HTMLElement;
    firstElement?.focus();
  } else {
    previousFocusRef.current?.focus();
  }
}, [isOpen]);
```

## Color Contrast

Ensure text has sufficient contrast:

- Normal text: Minimum 4.5:1 ratio
- Large text (18pt+): Minimum 3:1 ratio
- Use online contrast checkers to verify

## Images & Alt Text

```tsx
{
  /* Informative image */
}
<img src="image.png" alt="Description of image content" />;

{
  /* Decorative image */
}
<img src="image.png" alt="" aria-hidden="true" />;

{
  /* Complex image - provide long description */
}
<img src="chart.png" alt="Chart showing..." longdesc="url" />;
```

## Testing Checklist

When modifying or adding components:

- [ ] Can navigate entire component with keyboard
- [ ] Focus is always visible
- [ ] Form inputs have associated labels
- [ ] Error states are announced to screen readers
- [ ] Loading states are announced with aria-busy
- [ ] Buttons have descriptive labels
- [ ] Icons are hidden from screen readers with aria-hidden when needed
- [ ] Links open in same window or have "(opens in new window)" text
- [ ] Color is not the only indicator (add text/icons)
- [ ] All interactive elements are keyboard accessible

## Browser Extensions for Testing

- **Axe DevTools** - Automated accessibility testing
- **WAVE** - Web Accessibility Evaluation Tool
- **Lighthouse** - Built into Chrome DevTools
- **NVDA** / **JAWS** / **VoiceOver** - Screen reader testing

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN ARIA Authoring Practices](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)
- [React Accessibility](https://react.dev/learn/accessibility)
- [W3C WAI-ARIA](https://www.w3.org/WAI/standards-guidelines/aria/)

## Common Mistakes to Avoid

❌ Using `<div>` instead of semantic HTML
❌ Missing alt text on images
❌ Poor focus indicators
❌ Icon-only buttons without labels
❌ Relying on color alone to convey information
❌ Not managing focus in modals
❌ Missing form labels
❌ Not testing with actual screen readers
❌ Decorative content announced to screen readers
❌ Inaccessible keyboard shortcuts
