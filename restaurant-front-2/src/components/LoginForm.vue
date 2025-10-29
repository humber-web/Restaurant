<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { HTMLAttributes } from 'vue'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)

async function onSubmit() {
  isLoading.value = true
  error.value = null

  try {
    await authStore.login({ username: username.value, password: password.value })
    // Redirect to requested page or dashboard
    const nextPath = (route.query.next as string) || undefined
    if (nextPath) {
      await router.push(nextPath)
    } else {
      await router.push({ name: 'dashboard' })
    }
  } catch (err: any) {
    error.value = err?.message || 'Erro ao iniciar sessão'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div :class="cn('flex flex-col gap-6', props.class)">
    <Card>
      <CardHeader>
        <CardTitle>Iniciar sessão na sua conta</CardTitle>
        <CardDescription>
          Introduza o nome de utilizador e a palavra‑passe abaixo para iniciar sessão.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="onSubmit">
          <div class="flex flex-col gap-6">
            <div class="grid gap-3">
              <Label for="userName">Nome de utilizador</Label>
              <Input
                id="userName"
                type="text"
                placeholder="joaosilva"
                v-model="username"
                required
              />
            </div>
            <div class="grid gap-3">
              <div class="flex items-center">
                <Label for="password">Palavra‑passe</Label>
                <a
                  href="#"
                  class="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                >
                  Esqueceu a palavra‑passe?
                </a>
              </div>
              <Input id="password" type="password" v-model="password" required />
            </div>
            <div>
              <div v-if="error" class="text-sm text-destructive mb-2">{{ error }}</div>
              <Button type="submit" class="w-full" :disabled="isLoading">
                {{ isLoading ? 'A processar...' : 'Iniciar sessão' }}
              </Button>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
