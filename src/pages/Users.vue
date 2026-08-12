<script setup>
import { ref, onMounted } from 'vue'

const users = ref([])
const key = ref(localStorage.getItem('adminKey') || '')

async function load() {
  const res = await fetch('/api/admin/list', {
    headers: { 'X-Admin-Key': key.value }
  })
  users.value = await res.json()
}

function saveKey() {
  localStorage.setItem('adminKey', key.value)
}

async function removeUser(username) {
  await fetch(`/api/admin/remove/${username}`, {
    method: 'DELETE',
    headers: { 'X-Admin-Key': key.value }
  })
  load()
}

onMounted(load)
</script>

<template>
  <h1 class="text-2xl font-bold mb-4">Users</h1>

  <input v-model="key" placeholder="Admin Key" class="p-2 bg-gray-800 rounded" />
  <button @click="saveKey" class="ml-2 p-2 bg-blue-600 rounded">Save</button>

  <table class="mt-6 w-full">
    <tr class="text-left border-b border-gray-700">
      <th>Username</th>
      <th>Expiry</th>
      <th>Actions</th>
    </tr>

    <tr v-for="u in users" :key="u.username" class="border-b border-gray-800">
      <td>{{ u.username }}</td>
      <td>{{ u.expiry }}</td>
      <td>
        <button @click="removeUser(u.username)" class="p-2 bg-red-600 rounded">
          Delete
        </button>
      </td>
    </tr>
  </table>
</template>
