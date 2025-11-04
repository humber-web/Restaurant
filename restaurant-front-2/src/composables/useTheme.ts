import { ref, watch, onMounted } from 'vue'

type Theme = 'light' | 'dark'

const THEME_STORAGE_KEY = 'restaurant-theme'

export function useTheme() {
  const theme = ref<Theme>('light')

  // Initialize theme from localStorage or system preference
  const initializeTheme = () => {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as Theme | null

    if (savedTheme) {
      theme.value = savedTheme
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      theme.value = prefersDark ? 'dark' : 'light'
    }

    applyTheme(theme.value)
  }

  // Apply theme to document
  const applyTheme = (newTheme: Theme) => {
    const root = document.documentElement

    if (newTheme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }

  // Toggle between light and dark
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  // Set specific theme
  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme
  }

  // Watch for theme changes and persist
  watch(theme, (newTheme) => {
    applyTheme(newTheme)
    localStorage.setItem(THEME_STORAGE_KEY, newTheme)
  })

  // Listen for system preference changes
  onMounted(() => {
    initializeTheme()

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      // Only update if no saved preference exists
      if (!localStorage.getItem(THEME_STORAGE_KEY)) {
        theme.value = e.matches ? 'dark' : 'light'
      }
    })
  })

  return {
    theme,
    toggleTheme,
    setTheme,
    isDark: () => theme.value === 'dark',
  }
}
