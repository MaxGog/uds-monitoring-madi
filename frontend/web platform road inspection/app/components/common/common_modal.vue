<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container" :style="{ maxWidth: width }">
          
          <div class="modal-header">
            <div class="modal-title-area">
              <slot name="header">
                <h3 class="modal-title">{{ title }}</h3>
              </slot>
            </div>
            <button class="modal-close-btn" @click="$emit('close')" title="Закрыть">✕</button>
          </div>

          <div class="modal-body">
            <slot />
          </div>

          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
          
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  width: {
    type: String,
    default: '680px'
  }
})

defineEmits(['close'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  display: grid;
  place-items: center;
  padding: 32px 24px;
  z-index: 1000;
}

.modal-container {
  background: #ffffff;
  border: 1px solid #e1e3e8;
  border-radius: 8px;
  width: 100%;
  max-height: 85vh;
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.18), 0 2px 4px rgba(0, 0, 0, 0.14);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 28px;
  border-bottom: 1px solid #f3f2f1;
  gap: 16px;
}

.modal-title-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #242424;
}

.modal-close-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #616161;
  padding: 6px 10px;
  border-radius: 4px;
  transition: background 0.1s;
}
.modal-close-btn:hover {
  background: #f3f2f1;
  color: #242424;
}

.modal-body {
  padding: 24px 28px;
  overflow-y: auto;
  flex: 1;
  font-size: 14px;
  color: #242424;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-footer {
  padding: 18px 28px;
  background: #fbfbfb;
  border-top: 1px solid #f3f2f1;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>