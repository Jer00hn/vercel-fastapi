<script setup>
import { ref } from 'vue'

const username = ref('')
const days = ref(30)
const key = localStorage.getItem('adminKey')

async function submit() {
  await fetch('/api/admin/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Admin-Key': key
    },
    body: JSON.stringify({ username: username.value, days: days.value })
  })
  alert('OK')
}
</script>

<template>
  <h1 class="text-2xl font-bold mb-4">Add Subscription</h1>

  <div class="flex flex-col gap-4 w-64">
    <input v-model="username" placeholder="username" class="p-2 bg-gray-800 rounded" />
    <input v-model="days" type="number" class="p-2 bg-gray-800 rounded" />
    <button @click="submit" class="p-2 bg-green-600 rounded">Add</button>
  </div>
</template>
