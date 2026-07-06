import { computed, ref } from 'vue'
export interface ActVolumeRow {
    name: string
    plan: number
    fact: number
    unit: string
}

export interface MockAct {
    id: number
    number: string
    objectName: string
    type: string
    date: string
    contractor: string
    status: 'На утверждении' | 'Ожидает подписи' | 'Подписан'
    amount: string
    signedBy: string
    notes: string
    region: 'ЦАО' | 'САО' | 'ЮАО' | 'ЗАО' | 'ВАО'
    contractNumber: string
    planAmount: string
    vatAmount: string
    docUrl: string
    pdfUrl: string
    signDate: string
    volumes: ActVolumeRow[]
}

export interface MockWorkStatus {
    id: number
    objectName: string
    region: string
    stage: 'Проверка объемов' | 'Анализ отклонений' | 'Приемка работ' | 'Завершено'
    progress: string
    manager: string
    updatedAt: string
    nextAction: string
    hasDeviationAlert: boolean
    budgetAllocation: {
        total: string
        spent: string
        remaining: string
    }
    historyLog: Array<{ date: string; action: string; user: string }>
}

export interface MockRoadmapItem {
    id: number
    title: string
    region: 'ЦАО' | 'САО' | 'ЮАО' | 'ЗАО' | 'ВАО'
    startDate: string
    endDate: string
    phase: 'Разработка проекта' | 'Подготовка ИД' | 'Проверка согласований' | 'Утверждено'
    risk: 'Низкий' | 'Средний' | 'Высокий'
    progressPercentage: number
    area: number
    cost: number
    lastSource: 'Google Sheets' | 'Ручной ввод' | 'Интеграция API'
}

export interface MockTask {
    id: number
    title: string
    description: string
    completed: boolean
    status: 'Активная' | 'Внимание' | 'Критическая' | 'Выполнена'
    type: 'Проверка СМР' | 'Выгрузка актов' | 'Сверка реестра'
    objectTitle: string
    dueDate: string
    responsibleNames: string[]
    hasReminderTrigger: boolean
}

export interface MockUser {
    id: number
    fullName: string
    email: string
    role: 'Администратор' | 'Инспектор ОДХ' | 'Представитель подрядчика'
    regionAccess: string[]
    signatureId: string
}


const mockActsList: MockAct[] = [
    {
        id: 1,
        number: 'АКТ-2026-001',
        objectName: 'Капитальный ремонт ул. Тверская',
        type: 'Приёмка работ',
        date: '04.07.2026',
        contractor: 'ООО ТехСтрой',
        status: 'На утверждении',
        amount: '12 480 000 ₽',
        signedBy: 'Петров С. В.',
        notes: 'Пакет документов прошел первичную валидацию.',
        region: 'ЦАО',
        contractNumber: 'ГК-2026/09-ЦАО',
        planAmount: '12 500 000 ₽',
        vatAmount: '2 080 000 ₽',
        docUrl: '#',
        pdfUrl: '#',
        signDate: '—',
        volumes: [
            { name: 'Фрезерование асфальтобетонного покрытия', plan: 1200, fact: 1180, unit: 'м³' },
            { name: 'Укладка нижнего слоя покрытия из горячей смеси', plan: 450, fact: 450, unit: 'т' },
            { name: 'Укладка верхнего слоя (ЩМА-16) на ПБВ', plan: 450, fact: 442, unit: 'т' },
            { name: 'Замена бортового камня (гранит)', plan: 850, fact: 850, unit: 'п.м.' },
            { name: 'Ремонт смотровых колодцев', plan: 32, fact: 30, unit: 'шт' }
        ]
    },
    {
        id: 2,
        number: 'АКТ-2026-002',
        objectName: 'Реконструкция путепровода на Ленинградском шоссе',
        type: 'Технический контроль',
        date: '29.06.2026',
        contractor: 'АО МосДорСнаб',
        status: 'Ожидает подписи',
        amount: '45 120 000 ₽',
        signedBy: 'Иванов К. П.',
        notes: 'Требуется повторная инструментальная сверка объемов.',
        region: 'САО',
        contractNumber: 'ГК-2025/44-САО',
        planAmount: '45 120 000 ₽',
        vatAmount: '7 520 000 ₽',
        docUrl: '#',
        pdfUrl: '#',
        signDate: '—',
        volumes: [
            { name: 'Демонтаж деформационных швов путепровода', plan: 4, fact: 4, unit: 'компл' },
            { name: 'Устройство выравнивающего слоя из бетона B35', plan: 180, fact: 180, unit: 'м³' },
            { name: 'Гидроизоляция мостового полотна напыляемая', plan: 2450, fact: 2450, unit: 'м²' }
        ]
    }
]

const mockWorkStatusesList: MockWorkStatus[] = [
    {
        id: 1,
        objectName: 'Улица Тверская (Курс ремонта)',
        region: 'ЦАО',
        stage: 'Проверка объемов',
        progress: '75%',
        manager: 'Петров С. В.',
        updatedAt: '04.07.2026',
        nextAction: 'Выгрузка акта в Google Docs',
        hasDeviationAlert: true,
        budgetAllocation: { total: '12.5 млн ₽', spent: '9.3 млн ₽', remaining: '3.2 млн ₽' },
        historyLog: [
            { date: '01.07.2026', action: 'Инициация проверки СМР', user: 'Сидоров М. А.' },
            { date: '04.07.2026', action: 'Внесены фактические объемы фрезерования', user: 'Петров С. В.' }
        ]
    }
]

const mockRoadmapItemsList: MockRoadmapItem[] = [
    {
        id: 1,
        title: 'ДК Ремонт дорожного полотна ул. Тверская',
        region: 'ЦАО',
        startDate: '01.07.2026',
        endDate: '15.07.2026',
        phase: 'Проверка согласований',
        risk: 'Средний',
        progressPercentage: 65,
        area: 14500.25,
        cost: 12500000.0,
        lastSource: 'Google Sheets'
    }
]

const mockTasksList: MockTask[] = [
    {
        id: 1,
        title: 'Устранить расхождения по фрезерованию на Тверской',
        description: 'Объем фрезерования в акте №1 не бьется с геодезической съемкой.',
        completed: false,
        status: 'Внимание',
        type: 'Проверка СМР',
        objectTitle: 'ул. Тверская',
        dueDate: '08.07.2026',
        responsibleNames: ['Петров С. В.'],
        hasReminderTrigger: true
    }
]

const mockUsersList: MockUser[] = [
    {
        id: 1,
        fullName: 'Иванов Иван Иванович',
        email: 'ivanov@odh.mos.ru',
        role: 'Администратор',
        regionAccess: ['ЦАО', 'САО', 'ЮАО', 'ЗАО', 'ВАО'],
        signatureId: 'E-SIG-77-9921A'
    },
    {
        id: 2,
        fullName: 'Петров Сергей Владимирович',
        email: 'petrov.sv@odh.mos.ru',
        role: 'Инспектор ОДХ',
        regionAccess: ['ЦАО'],
        signatureId: 'E-SIG-77-1044B'
    }
]

const acts = ref<MockAct[]>(mockActsList)
const workStatuses = ref<MockWorkStatus[]>(mockWorkStatusesList)
const roadmapItems = ref<MockRoadmapItem[]>(mockRoadmapItemsList)
const tasks = ref<MockTask[]>(mockTasksList)
const users = ref<MockUser[]>(mockUsersList)

export function useMockData() {
    return {
        acts,
        workStatuses,
        roadmapItems,
        tasks,
        users,
        types: computed(() => Array.from(new Set(acts.value.map(a => a.type)))),
        regions: computed(() => Array.from(new Set(acts.value.map(a => a.region))))
    }
}