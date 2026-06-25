<template>
  <div class="auth-layout">
    <div class="auth-blur-bg"></div>
    <main class="auth-content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.auth-layout {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
  font-family: var(--fluent-font, 'Segoe UI', -apple-system, sans-serif);
  overflow: hidden;
}

.auth-blur-bg {
  position: absolute;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 120, 212, 0.15) 0%, rgba(255, 255, 255, 0) 70%);
  top: -10%;
  left: -10%;
  z-index: 1;
  pointer-events: none;
}
</style>