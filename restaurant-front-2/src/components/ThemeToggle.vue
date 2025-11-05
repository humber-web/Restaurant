<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>

<template>
  <Button
    variant="ghost"
    size="icon"
    @click="themeStore.toggleTheme"
    :aria-label="themeStore.theme === 'light' ? 'Mudar para tema escuro' : 'Mudar para tema claro'"
  >
    <Sun v-if="themeStore.theme === 'light'" class="h-5 w-5" />
    <Moon v-else class="h-5 w-5" />
  </Button>
</template>
