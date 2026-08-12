<template>
  <div class="p-6">
    <nav class="flex gap-4 mb-6 text-lg">
      <router-link to="/">Dashboard</router-link>
      <router-link to="/users">Users</router-link>
      <router-link to="/add">Add</router-link>
    </nav>

    <router-view />
  </div>
</template>
