<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/composables/useTheme'

const { theme, toggleTheme } = useTheme()
</script>

<template>
  <Button
    variant="ghost"
    size="icon"
    @click="toggleTheme"
    :aria-label="theme === 'light' ? 'Mudar para tema escuro' : 'Mudar para tema claro'"
  >
    <Sun v-if="theme === 'light'" class="h-5 w-5" />
    <Moon v-else class="h-5 w-5" />
  </Button>
</template>
