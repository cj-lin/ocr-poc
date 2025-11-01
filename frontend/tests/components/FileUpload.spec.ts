import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FileUpload from '~/components/FileUpload.vue'

describe('FileUpload Component', () => {
  it('renders upload area', () => {
    const wrapper = mount(FileUpload)
    expect(wrapper.find('[data-testid="upload-area"]').exists()).toBe(true)
  })

  it('validates file size (max 10MB)', () => {
    const wrapper = mount(FileUpload)
    
    // Create a mock file that's too large (15MB)
    const largeFile = new File(['x'.repeat(15 * 1024 * 1024)], 'large.jpg', {
      type: 'image/jpeg',
    })

    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', {
      value: [largeFile],
      writable: false,
    })

    input.trigger('change')

    // Should show error message
    expect(wrapper.emitted('error')).toBeTruthy()
  })

  it('validates file type (JPG, PNG, PDF only)', () => {
    const wrapper = mount(FileUpload)

    // Create invalid file type
    const invalidFile = new File(['content'], 'document.txt', {
      type: 'text/plain',
    })

    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', {
      value: [invalidFile],
      writable: false,
    })

    input.trigger('change')

    // Should show error message
    expect(wrapper.emitted('error')).toBeTruthy()
  })

  it('accepts valid file types', () => {
    const wrapper = mount(FileUpload)

    const validFiles = [
      new File(['content'], 'image.jpg', { type: 'image/jpeg' }),
      new File(['content'], 'image.png', { type: 'image/png' }),
      new File(['content'], 'document.pdf', { type: 'application/pdf' }),
    ]

    validFiles.forEach((file) => {
      const input = wrapper.find('input[type="file"]')
      Object.defineProperty(input.element, 'files', {
        value: [file],
        writable: false,
      })

      input.trigger('change')

      // Should emit fileSelected event
      expect(wrapper.emitted('fileSelected')).toBeTruthy()
    })
  })

  it('handles drag and drop', async () => {
    const wrapper = mount(FileUpload)
    const dropZone = wrapper.find('[data-testid="upload-area"]')

    // Simulate drag enter
    await dropZone.trigger('dragenter')
    expect(wrapper.vm.isDragging).toBe(true)

    // Simulate drag leave
    await dropZone.trigger('dragleave')
    expect(wrapper.vm.isDragging).toBe(false)
  })

  it('shows upload progress', async () => {
    const wrapper = mount(FileUpload, {
      props: {
        isUploading: true,
        progress: 50,
      },
    })

    expect(wrapper.find('[data-testid="progress-bar"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('50%')
  })
})
