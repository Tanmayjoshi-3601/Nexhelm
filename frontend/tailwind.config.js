/** @type {import('tailwindcss').Config} */
module.exports = {
    // Tell Tailwind where to look for classes
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",  // All React files
    ],
    theme: {
        extend: {
            // Custom colors for financial theme
            colors: {
                'nexhelm-blue': '#1e40af',
                'nexhelm-dark': '#1e293b',
                'opportunity-gold': '#fbbf24',
            },
            // Custom animations
            animation: {
                'slide-in': 'slideIn 0.3s ease-out',
                'pulse-soft': 'pulseSoft 2s infinite',
            },
            keyframes: {
                slideIn: {
                    '0%': { transform: 'translateX(100%)', opacity: '0' },
                    '100%': { transform: 'translateX(0)', opacity: '1' },
                },
                pulseSoft: {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.8' },
                },
            },
        },
    },
    plugins: [],
}