import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EditableForm from '~/components/EditableForm.vue'
import type { IdCardInfo } from '~/types'

describe('EditableForm Component', () => {
  const mockData: IdCardInfo = {
    name: '王小明',
    id_number: 'A123456789',
    birth_date: '80/05/20',
    gender: '男',
    issue_date: '95/12/01',
    issue_location: '台北市',
    confidence_score: 0.95,
  }

  it('renders all fields', () => {
    const wrapper = mount(EditableForm, {
      props: {
        data: mockData,
      },
    })

    expect(wrapper.text()).toContain('姓名')
    expect(wrapper.text()).toContain('身分證字號')
    expect(wrapper.text()).toContain('出生日期')
    expect(wrapper.text()).toContain('性別')
    expect(wrapper.text()).toContain('發證日期')
    expect(wrapper.text()).toContain('發證地點')
  })

  it('displays field values', () => {
    const wrapper = mount(EditableForm, {
      props: {
        data: mockData,
      },
    })

    expect(wrapper.find('input[name="name"]').element.value).toBe('王小明')
    expect(wrapper.find('input[name="id_number"]').element.value).toBe('A123456789')
    expect(wrapper.find('input[name="birth_date"]').element.value).toBe('80/05/20')
  })

  it('allows editing fields', async () => {
    const wrapper = mount(EditableForm, {
      props: {
        data: mockData,
      },
    })

    const nameInput = wrapper.find('input[name="name"]')
    await nameInput.setValue('李小華')

    expect(wrapper.emitted('update')).toBeTruthy()
    expect(wrapper.emitted('update')[0][0]).toHaveProperty('name', '李小華')
  })

  it('validates ID number format', async () => {
    const wrapper = mount(EditableForm, {
      props: {
        data: mockData,
      },
    })

    const idInput = wrapper.find('input[name="id_number"]')
    await idInput.setValue('123')  // Invalid format

    // Should show validation error
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })

  it('validates date format (ROC calendar)', async () => {
    const wrapper = mount(EditableForm, {
      props: {
        data: mockData,
      },
    })

    const dateInput = wrapper.find('input[name="birth_date"]')
    await dateInput.setValue('2000/05/20')  // Should be ROC format

    // Should show validation error
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })

  it('shows confidence score when available', () => {
    const wrapper = mount(EditableForm, {
      props: {
        data: mockData,
      },
    })

    expect(wrapper.text()).toContain('95%')
  })

  it('handles missing confidence score', () => {
    const dataWithoutScore = { ...mockData }
    delete dataWithoutScore.confidence_score

    const wrapper = mount(EditableForm, {
      props: {
        data: dataWithoutScore,
      },
    })

    // Should not crash, just not show confidence
    expect(wrapper.find('[data-testid="confidence"]').exists()).toBe(false)
  })
})
