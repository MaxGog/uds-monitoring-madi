import { computed, ref } from 'vue'

import type { Act } from '~/types/act'
import type { Object as ObjectItem } from '~/types/object'
import type { Roadmap } from '~/types/roadmap'
import { type Task, TaskStatus, TaskType } from '~/types/task'
import type { User } from '~/types/user'
import type { Work } from '~/types/work'

const mockActsList: Act[] = [
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

const mockObjectsList = ref<ObjectItem[]>([
    {
        id: 1,
        title: 'Капитальный ремонт ул. Тверская (от Манежной пл. до Настасьинского пер.)',
        region: 'ЦАО',
        status: 'Активный',
        contractor: 'ООО ТехСтрой',
        executor: 'Объединение административно-технических инспекций (ОАТИ)',
        progressSMR: 72,
        source: 'АСУ ПРИЗ',
        sourceLabel: 'Интеграция с АСУ ПРИЗ включена',
        contractNumber: 'К-77-0021/2026',
        contractDate: '12.01.2026',
        contractAmount: '154 200 000 ₽',
        spentAmount: '111 024 000 ₽',
        remainingAmount: '43 176 000 ₽',
        hasActs: true,
        connectedActsCount: 3,
        historyLog: [
            { date: '04.07.2026', action: 'Загружен новый Акт приемки №1', user: 'Петров С. В.' },
            { date: '25.06.2026', action: 'Актуализирован физический объем (Фрезерование)', user: 'Иванов И. И.' },
            { date: '10.06.2026', action: 'Объект переведен в статус "Активный"', user: 'Сидоров А. П.' }
        ]
    },
    {
        id: 2,
        title: 'Реконструкция путепровода Ленинградское шоссе на пересечении с МЦД-3',
        region: 'САО',
        status: 'На проверке',
        contractor: 'АО МосИнжПроект',
        executor: 'Мосгосстройнадзор',
        progressSMR: 45,
        source: 'ЕАИСТ',
        sourceLabel: 'Синхронизировано с ЕАИСТ',
        contractNumber: 'ГК-2026-991',
        contractDate: '05.02.2026',
        contractAmount: '420 500 000 ₽',
        spentAmount: '189 225 000 ₽',
        remainingAmount: '231 275 000 ₽',
        hasActs: true,
        connectedActsCount: 1,
        historyLog: [
            { date: '29.06.2026', action: 'Инициирован технический контроль геодезистов', user: 'Петров С. В.' }
        ]
    },
    {
        id: 3,
        title: 'Благоустройство территории и ОДХ в районе Нагатинская Пойма',
        region: 'ЮАО',
        status: 'Планирование',
        contractor: 'ООО СпецДорСервис',
        executor: 'Департамент капитального ремонта',
        progressSMR: 5,
        source: 'Ручной ввод',
        sourceLabel: 'Локальный объект (без внешних систем)',
        contractNumber: 'ВН-9922-АК',
        contractDate: '18.05.2026',
        contractAmount: '89 000 000 ₽',
        spentAmount: '4 450 000 ₽',
        remainingAmount: '84 550 000 ₽',
        hasActs: false,
        connectedActsCount: 0,
        historyLog: [
            { date: '30.06.2026', action: 'Создана карточка планирования объекта', user: 'Иванов И. И.' }
        ]
    },
    {
        id: 4,
        title: 'Строительство дублёра Кутузовского проспекта (участок от МКАД до Минского шоссе)',
        region: 'ЗАО',
        status: 'Завершено',
        contractor: 'АО Дороги и Мосты',
        executor: 'Ростехнадзор',
        progressSMR: 100,
        source: 'АСУ ПРИЗ',
        sourceLabel: 'Архивные данные АСУ ПРИЗ',
        contractNumber: 'К-77-0001/2025',
        contractDate: '10.03.2025',
        contractAmount: '850 000 000 ₽',
        spentAmount: '850 000 000 ₽',
        remainingAmount: '0 ₽',
        hasActs: true,
        connectedActsCount: 12,
        historyLog: [
            { date: '03.07.2026', action: 'Объект успешно закрыт в системе, все акты подписаны', user: 'Морозов А. А.' }
        ]
    }
])

const mockWorkStatusesList: Work[] = [
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

export const mockRoadmapItemsList: Roadmap[] = [
    {
        id: 1,
        title: 'Капитальный ремонт ул. Тверская (от Манежной пл. до Триумфальной пл.)',
        region: 'ЦАО',
        startDate: '10.05.2026',
        endDate: '25.08.2026',
        phase: 'Разработка проекта',
        risk: 'Высокий',
        riskDescription: 'Обнаружено смещение подземных коммуникаций, не указанных на архивных планах Мосгоргеотреста.',
        manager: 'Петров С. В.',
        budget: '142 500 000 ₽',
        objectId: 1,
        progressPercentage: 0,
        area: 0,
        cost: 0,
        lastSource: 'Ручной ввод',
        milestones: [],
        responsibleManager: 'Петров С. В.',
        hasRiskAlert: true
    },
    {
        id: 2,
        title: 'Реконструкция развязки на пересечении Ленинградского шоссе и ул. Серегина',
        region: 'САО',
        startDate: '01.03.2026',
        endDate: '15.11.2026',
        phase: 'Подготовка ИД',
        risk: 'Средний',
        riskDescription: 'Задержка согласования временной схемы организации дорожного движения (ОДД).',
        manager: 'Иванов И. И.',
        budget: '289 000 000 ₽',
        progressPercentage: 20,
        objectId: 2,
        area: 0,
        cost: 0,
        lastSource: 'Ручной ввод',
        milestones: [],
        responsibleManager: 'Иванов И. И.',
        hasRiskAlert: false
    },
    {
        id: 3,
        title: 'Устройство велодорожек и благоустройство Нагатинской набережной',
        region: 'ЮАО',
        startDate: '01.06.2026',
        endDate: '01.09.2026',
        phase: 'Проверка согласований',
        risk: 'Низкий',
        riskDescription: 'Идут плановые работы, поставка малых архитектурных форм без задержек.',
        manager: 'Сидоров К. А.',
        budget: '64 200 000 ₽',
        progressPercentage: 60,
        objectId: 3,
        area: 0,
        cost: 0,
        lastSource: 'Ручной ввод',
        milestones: [],
        responsibleManager: 'Сидоров К. А.',
        hasRiskAlert: false
    }
]

const mockTasksList: Task[] = [
    {
        id: 1,
        title: 'Устранить расхождения по фрезерованию на Тверской',
        description: 'Объем фрезерования в акте №1 не бьется с геодезической съемкой.',
        completed: false,
        status: TaskStatus.IN_PROGRESS,
        type: TaskType.CMR_CHECK,
        objectTitle: 'ул. Тверская',
        dueDate: '08.07.2026',
        responsibleNames: ['Петров С. В.'],
        hasReminderTrigger: true
    }
]

const mockUsersList: User[] = [
    {
        id: '1',
        username: 'ivanov',
        email: 'ivanov@odh.mos.ru',
        role: 'Администратор',
        company: 'ГБУ Автомобильные дороги',
        position: 'Руководитель проекта',
        status: 'Активный'
    },
    {
        id: '2',
        username: 'petrov_sv',
        email: 'petrov.sv@odh.mos.ru',
        role: 'Инспектор ОДХ',
        company: 'ОДХ ЦАО',
        position: 'Инспектор',
        status: 'Активный'
    }
]

const acts = ref<Act[]>(mockActsList)
const workStatuses = ref<Work[]>(mockWorkStatusesList)
const roadmapItems = ref<Roadmap[]>(mockRoadmapItemsList)
const tasks = ref<Task[]>(mockTasksList)
const users = ref<User[]>(mockUsersList)

const objects = mockObjectsList

const addObject = (newObj: Omit<ObjectItem, 'id' | 'hasActs' | 'connectedActsCount' | 'historyLog'>) => {
    const id = mockObjectsList.value.length + 1
    mockObjectsList.value.push({
        ...newObj,
        id,
        hasActs: false,
        connectedActsCount: 0,
        historyLog: [{ date: new Date().toLocaleDateString('ru-RU'), action: 'Объект зарегистрирован в системе', user: 'Иванов Иван' }]
    })
}

const addRoadmapItem = (newItem: Omit<Roadmap, 'id' | 'progressPercentage' | 'hasRiskAlert'>) => {
    const id = roadmapItems.value.length + 1
    roadmapItems.value.push({
        ...newItem,
        id,
        progressPercentage: 0,
        hasRiskAlert: false
    })

    const targetObj = objects.value.find(o => o.id === newItem.objectId)
    if (targetObj) {
        targetObj.historyLog.unshift({
            date: new Date().toLocaleDateString('ru-RU'),
            action: `Сформирована новая дорожная карта (ДК-${id})`,
            user: 'Текущий пользователь'
        })
    }
}

export function useMockData() {
    return {
        acts,
        workStatuses,
        roadmapItems,
        tasks,
        users,
        types: computed(() => Array.from(new Set(acts.value.map(a => a.type)))),
        regions: computed(() => Array.from(new Set(acts.value.map(a => a.region)))),
        objects,
        addObject,
        addRoadmapItem
    }
}