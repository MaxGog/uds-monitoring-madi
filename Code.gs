/**
 * Двухэтапное формирование актов из Google Sheets
 * + загрузка файлов / ZIP и вывод списка на отдельный лист
 *
 * УСЛОВИЯ:
 * - A -> (Наименование объекта)
 * - B -> (Округ)
 * - N -> {{ACT_DATE}}
 * - C:M -> 11 строк таблицы по порядку
 * - одно и то же значение пишется в План и Фактический
 * - если значение = 0, пусто, "0,0", "0.0" и т.п. -> соответствующая строка удаляется
 *
 * ВАЖНО:
 * 1) TEMPLATE_DOC_ID уже подставлен
 * 2) Для формирования актов используется стандартный DocumentApp.
 *    Advanced service Google Docs API не требуется.
 */

/*************** НАСТРОЙКИ ***************/
const SPREADSHEET_ID = '1Io6Kfj1i-fhMh4BnzNnPBguqq0zX8qyVU3N7STbfvr4';
const SHEET_NAME = 'Объемы'; // лист-источник для формирования актов
const TEMPLATE_DOC_ID = '1V-RIFMc0arHeO58PnGpdawTXNah9SM0XJHCVEMUWM3w';

const ROOT_FOLDER_NAME = 'Сформированные акты';
// Папка с уже сформированными актами, которую нужно связать с карточками сайта
const DOCS_FOLDER_NAME = 'Google Docs';
const PDF_FOLDER_NAME = 'PDF';

const FILES_LIST_SHEET_NAME = 'Список_файлов';
const UPLOADS_FOLDER_NAME = 'Загруженные файлы для актов';
const PDF_PAGES_SHEET_NAME = 'PDF_страницы';
const PDF_CACHE_KEY = 'pdf_pages_cache_v2';
const PDF_SCAN_BATCH_SIZE = 15; // можно 10-20

const CREATE_BATCH_SIZE = 50;
const EXPORT_BATCH_SIZE = 50;

const MAX_UNZIP_SIZE_BYTES = 10 * 1024 * 1024; // 10 МБ
const DRIVE_SCAN_BATCH_WRITE = 500;

// Таблица в шаблоне
const TEMPLATE_TABLE_INDEX = 0;

// Индексы колонок в таблице документа
const DOC_COL_PLAN = 2;
const DOC_COL_FACT = 3;

// 0-1 = заголовки таблицы, 2-12 = 11 строк работ
const TABLE_DATA_START_ROW = 2;

// Столбцы Google Sheets: A=0, B=1, C=2 ... M=12, N=13
const SHEET_WORK_START_COL = 2; // C
const SHEET_WORK_END_COL = 12;  // M
const SHEET_DATE_COL = 13;      // N



/*************** ПОЛЬЗОВАТЕЛИ И РОЛИ ***************/
const USERS_SHEET_NAME = 'Пользователи';
const USER_ROLE_ADMIN = 'Администратор';
const USER_ROLE_VIEW = 'Просмотр';
const USER_STATUS_ACTIVE = 'Активен';
const USERS_HEADERS = ['Email','ФИО','Должность','Отдел','Роль','Статус','Последний вход'];

function getCurrentUserProfile() {
  return requireActiveUser_();
}

function requireActiveUser_() {
  const email = getActiveUserEmail_();
  if (!email) {
    throw new Error('Не удалось определить Google-аккаунт пользователя. Проверьте, что веб-приложение опубликовано с доступом пользователя и открыт вход в Google.');
  }

  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = getOrCreateUsersSheet_(ss, email);
  const values = sheet.getDataRange().getValues();
  const normalizedEmail = normalizeEmail_(email);

  for (let i = 1; i < values.length; i++) {
    const rowEmail = normalizeEmail_(values[i][0]);
    if (rowEmail === normalizedEmail) {
      const status = String(values[i][5] || '').trim() || USER_STATUS_ACTIVE;
      if (normalizeWeb_(status) !== normalizeWeb_(USER_STATUS_ACTIVE)) {
        throw new Error('Учетная запись отключена. Обратитесь к администратору платформы.');
      }
      const role = normalizeUserRole_(values[i][4]);
      const rowNumber = i + 1;
      sheet.getRange(rowNumber, 7).setValue(new Date());
      return {
        email: email,
        fullName: String(values[i][1] || email).trim(),
        position: String(values[i][2] || '').trim(),
        department: String(values[i][3] || '').trim(),
        role: role,
        status: status,
        rowNumber: rowNumber,
        isAdmin: role === USER_ROLE_ADMIN,
        isReadOnly: role === USER_ROLE_VIEW
      };
    }
  }

  throw new Error('Пользователь ' + email + ' не найден в листе "' + USERS_SHEET_NAME + '". Обратитесь к администратору платформы.');
}

function requireAdmin_() {
  const user = requireActiveUser_();
  if (user.role !== USER_ROLE_ADMIN) {
    throw new Error('Недостаточно прав. Действие доступно только роли "' + USER_ROLE_ADMIN + '".');
  }
  return user;
}

function getActiveUserEmail_() {
  const active = String(Session.getActiveUser().getEmail() || '').trim();
  if (active) return active;
  return String(Session.getEffectiveUser().getEmail() || '').trim();
}

function getOrCreateUsersSheet_(ss, currentEmail) {
  let sheet = ss.getSheetByName(USERS_SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(USERS_SHEET_NAME);

  if (sheet.getLastRow() === 0 || !String(sheet.getRange(1, 1).getValue() || '').trim()) {
    sheet.getRange(1, 1, 1, USERS_HEADERS.length).setValues([USERS_HEADERS]);
    sheet.getRange(1, 1, 1, USERS_HEADERS.length).setFontWeight('bold').setBackground('#f1efff');
  }

  // Если лист только создан и пользователей нет, первый вошедший пользователь становится администратором.
  if (sheet.getLastRow() < 2 && currentEmail) {
    sheet.appendRow([currentEmail, currentEmail, '', '', USER_ROLE_ADMIN, USER_STATUS_ACTIVE, new Date()]);
  }

  return sheet;
}

function normalizeEmail_(email) {
  return String(email || '').trim().toLowerCase();
}

function normalizeUserRole_(role) {
  const value = String(role || '').trim();
  if (normalizeWeb_(value) === normalizeWeb_(USER_ROLE_ADMIN)) return USER_ROLE_ADMIN;
  return USER_ROLE_VIEW;
}

function getUsersData() {
  requireAdmin_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = getOrCreateUsersSheet_(ss, getActiveUserEmail_());
  const values = sheet.getDataRange().getDisplayValues();
  return values.slice(1).filter(r => r[0]).map((r, idx) => ({
    rowNumber: idx + 2,
    email: String(r[0] || '').trim(),
    fullName: String(r[1] || '').trim(),
    position: String(r[2] || '').trim(),
    department: String(r[3] || '').trim(),
    role: normalizeUserRole_(r[4]),
    status: String(r[5] || USER_STATUS_ACTIVE).trim(),
    lastLogin: String(r[6] || '').trim()
  }));
}

function saveUserAccount(payload) {
  requireAdmin_();
  payload = payload || {};
  const email = normalizeEmail_(payload.email);
  if (!email) throw new Error('Укажите Email пользователя.');

  const role = normalizeUserRole_(payload.role);
  const status = String(payload.status || USER_STATUS_ACTIVE).trim() || USER_STATUS_ACTIVE;
  const row = [
    email,
    String(payload.fullName || '').trim(),
    String(payload.position || '').trim(),
    String(payload.department || '').trim(),
    role,
    status,
    ''
  ];

  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = getOrCreateUsersSheet_(ss, getActiveUserEmail_());
  const values = sheet.getDataRange().getValues();
  for (let i = 1; i < values.length; i++) {
    if (normalizeEmail_(values[i][0]) === email) {
      const lastLogin = values[i][6] || '';
      row[6] = lastLogin;
      sheet.getRange(i + 1, 1, 1, USERS_HEADERS.length).setValues([row]);
      logPlatformChange_('users', 'saveUser', email, {
        rowNumber: i + 1,
        email: row[0],
        fullName: row[1],
        position: row[2],
        department: row[3],
        role: row[4],
        status: row[5],
        lastLogin: row[6]
      });
      return {success:true, rowNumber:i + 1, updated:true};
    }
  }
  sheet.appendRow(row);
  const rowNumber = sheet.getLastRow();
  logPlatformChange_('users', 'saveUser', email, {
    rowNumber: rowNumber,
    email: row[0],
    fullName: row[1],
    position: row[2],
    department: row[3],
    role: row[4],
    status: row[5],
    lastLogin: row[6]
  });
  return {success:true, rowNumber:rowNumber, created:true};
}

function setUserAccountStatus(rowNumber, status) {
  requireAdmin_();
  rowNumber = Number(rowNumber);
  if (!rowNumber || rowNumber < 2) throw new Error('Некорректная строка пользователя.');
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = getOrCreateUsersSheet_(ss, getActiveUserEmail_());
  sheet.getRange(rowNumber, 6).setValue(String(status || USER_STATUS_ACTIVE).trim());
  return {success:true};
}


/*************** ЖИВАЯ СИНХРОНИЗАЦИЯ ПЛАТФОРМЫ ***************/
const LIVE_CHANGES_SHEET_NAME = 'Журнал_изменений';

function getPlatformChangesSince(lastSyncTs) {
  const user = requireActiveUser_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(LIVE_CHANGES_SHEET_NAME);
  const nowIso = new Date().toISOString();
  if (!sheet || sheet.getLastRow() < 2) {
    return { success: true, changes: [], lastSync: nowIso };
  }

  const lastDate = lastSyncTs ? new Date(lastSyncTs) : new Date(0);
  const values = sheet.getRange(2, 1, sheet.getLastRow() - 1, 8).getValues();
  const changes = values
    .filter(r => r[1] && new Date(r[1]) > lastDate)
    .filter(r => String(r[6] || '') !== String(user.email || ''))
    .map(r => ({
      id: r[0],
      timestamp: r[1] instanceof Date ? r[1].toISOString() : String(r[1] || ''),
      module: r[2],
      action: r[3],
      objectKey: r[4],
      userName: r[5],
      userEmail: r[6],
      data: safeParseJson_(r[7])
    }));

  return { success: true, changes: changes, lastSync: nowIso };
}

function logPlatformChange_(moduleName, action, objectKey, data) {
  try {
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = getOrCreateLiveChangesSheet_(ss);
    const user = getCurrentUserProfileSafe_();
    sheet.appendRow([
      Utilities.getUuid(),
      new Date(),
      String(moduleName || ''),
      String(action || ''),
      String(objectKey || ''),
      user.fullName || user.email || '',
      user.email || '',
      JSON.stringify(data || {})
    ]);
    trimLiveChangesLog_(sheet);
  } catch (e) {
    // Живая синхронизация не должна ломать основное действие пользователя.
  }
}

function getOrCreateLiveChangesSheet_(ss) {
  let sheet = ss.getSheetByName(LIVE_CHANGES_SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(LIVE_CHANGES_SHEET_NAME);
    sheet.getRange(1, 1, 1, 8).setValues([[
      'ID изменения',
      'Дата/время',
      'Модуль',
      'Действие',
      'Ключ объекта',
      'Пользователь',
      'Email',
      'Данные JSON'
    ]]);
    sheet.getRange(1, 1, 1, 8).setFontWeight('bold').setBackground('#f1efff');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function trimLiveChangesLog_(sheet) {
  const maxRows = 1200;
  const lastRow = sheet.getLastRow();
  if (lastRow > maxRows) {
    sheet.deleteRows(2, lastRow - maxRows);
  }
}

function safeParseJson_(value) {
  try {
    return JSON.parse(String(value || '{}'));
  } catch (e) {
    return {};
  }
}

function getCurrentUserProfileSafe_() {
  try {
    const u = getCurrentUserProfile_();
    return { email: u.email || getActiveUserEmail_(), fullName: u.fullName || u.email || '' };
  } catch (e) {
    try {
      const email = getActiveUserEmail_();
      return { email: email, fullName: email };
    } catch (err) {
      return { email: '', fullName: '' };
    }
  }
}


/*************** ВЕБ-САЙТ: НАСТРОЙКИ МОНИТОРИНГА ***************/
const SHEET_STATUS = 'Статус загрузки актов';
const SHEET_CONTRACTS = 'Контракты';
const SHEET_VOLUMES = 'Объемы';
const ACTS_FOLDER_ID = '1EuqDsMXrLQU_QrCoYRTilAMyXbJteBHu';
const PDF_MAIN_3P_FOLDER_ID = '1DiXbYegVav5bJ2J_tVeYbwr09Dd6wazz';
const PDF_APPEND_4P_FOLDER_ID = '1mfnokqbTvEdRqCwCHNIDuJPsZl4ZtA20';
const FILES_LIST_SHEET = FILES_LIST_SHEET_NAME;
const AIS_UPDATE_COLUMN = 10; // J: Обновление данных в АИС
const AIS_UPDATE_DONE = 'Данные обновлены';
const AIS_UPDATE_REQUIRED = 'Требуется обновление';

function doGet() {
  return HtmlService
    .createHtmlOutputFromFile('Index')
    .setTitle('Мониторинг загрузки актов')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function getDashboardData() {
  const currentUser = requireActiveUser_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const statusSheet = ss.getSheetByName(SHEET_STATUS);
  const contractsSheet = ss.getSheetByName(SHEET_CONTRACTS);
  const volumesSheet = ss.getSheetByName(SHEET_VOLUMES);
  return {
    currentUser: currentUser,
    status: readStatusSheetWeb_(statusSheet),
    contracts: readContractsSheetWeb_(contractsSheet),
    volumes: readVolumesSheetWeb_(volumesSheet),
    actFiles: getActFilesFromListFast_()
  };
}

function readStatusSheetWeb_(sheet) {
  if (!sheet) throw new Error('Лист "' + SHEET_STATUS + '" не найден.');
  ensureAisUpdateColumnWeb_(sheet);
  const values = sheet.getDataRange().getDisplayValues();
  return values.slice(2).filter(r => r[0]).map(r => {
    const uploadStatus = String(r[4] || '').trim();
    const storedAisStatus = String(r[9] || '').trim();
    const autoUpdated = isTrueWeb_(uploadStatus);
    const aisUpdateStatus = autoUpdated ? AIS_UPDATE_DONE : normalizeAisUpdateStatusWeb_(storedAisStatus);
    return {
      objectName: String(r[0] || '').trim(),
      program: String(r[1] || '').trim(),
      geometryStatus: String(r[2] || '').trim(),
      actStatus: String(r[3] || '').trim(),
      uploadStatus: uploadStatus,
      cardStatus: String(r[5] || '').trim(),
      contractor: String(r[6] || '').trim(),
      executor: String(r[7] || '').trim(),
      district: String(r[8] || '').trim(),
      aisUpdateStatus: aisUpdateStatus,
      aisUpdate: aisUpdateStatus === AIS_UPDATE_DONE
    };
  });
}

function readContractsSheetWeb_(sheet) {
  if (!sheet) return [];
  const values = sheet.getDataRange().getValues();
  return values.slice(3).filter(r => r[0]).map(r => ({
    contractor: String(r[0] || '').trim(),
    contractNumber: String(r[1] || '').trim(),
    contractDate: formatDateWeb_(r[2]),
    subject: String(r[3] || '').trim(),
    customer: String(r[4] || '').trim()
  }));
}

function readVolumesSheetWeb_(sheet) {
  if (!sheet) return [];
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];

  const workHeaders = sheet.getRange(1, SHEET_WORK_START_COL + 1, 1, SHEET_WORK_END_COL - SHEET_WORK_START_COL + 1)
    .getDisplayValues()[0]
    .map(h => String(h || '').replace(/\s+/g, ' ').trim());

  const values = sheet.getRange(2, 1, lastRow - 1, Math.max(sheet.getLastColumn(), 15)).getDisplayValues();
  return values.filter(r => r[0]).map(r => {
    const workItems = [];
    for (let col = SHEET_WORK_START_COL; col <= SHEET_WORK_END_COL; col++) {
      const rawValue = String(r[col] || '').trim();
      const numericValue = numWeb_(rawValue);
      if (numericValue > 0) {
        workItems.push({
          name: workHeaders[col - SHEET_WORK_START_COL] || ('Вид работ ' + (col - SHEET_WORK_START_COL + 1)),
          value: rawValue || String(numericValue)
        });
      }
    }
    return {
      objectName: String(r[0] || '').trim(),
      district: String(r[1] || '').trim(),
      workItems: workItems,
      actDate: formatDateWeb_(r[13]),
      contractor: String(r[14] || '').trim(),
      road: numWeb_(r[2]), sidewalk: numWeb_(r[3]), roadCurb: numWeb_(r[4]), graniteCurb: numWeb_(r[5]),
      manhole: numWeb_(r[6]), lawn: numWeb_(r[7]), pavilion: numWeb_(r[8]), lightingPole: numWeb_(r[9]),
      lamp: numWeb_(r[10]), urn: numWeb_(r[11]), bench: numWeb_(r[12])
    };
  });
}

function updateObjectStatuses(objectName, statuses) {
  requireAdmin_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(SHEET_STATUS);
  if (!sheet) throw new Error('Лист "' + SHEET_STATUS + '" не найден.');
  ensureAisUpdateColumnWeb_(sheet);
  const values = sheet.getDataRange().getValues();
  for (let i = 2; i < values.length; i++) {
    const currentObject = String(values[i][0] || '').trim();
    if (normalizeWeb_(currentObject) === normalizeWeb_(objectName)) {
      const rowNumber = i + 1;
      sheet.getRange(rowNumber, 3, 1, 4).setValues([[
        statuses.geometryStatus || '',
        statuses.actStatus || '',
        statuses.uploadStatus || '',
        statuses.cardStatus || ''
      ]]);

      let aisUpdateStatus = normalizeAisUpdateStatusWeb_(String(values[i][AIS_UPDATE_COLUMN - 1] || '').trim());
      if (isTrueWeb_(statuses.uploadStatus)) {
        aisUpdateStatus = AIS_UPDATE_DONE;
        sheet.getRange(rowNumber, AIS_UPDATE_COLUMN).setValue(AIS_UPDATE_DONE);
      }

      logPlatformChange_('monitoring', 'statusUpdate', objectName, {
        objectName: objectName,
        rowNumber: rowNumber,
        geometryStatus: statuses.geometryStatus || '',
        actStatus: statuses.actStatus || '',
        uploadStatus: statuses.uploadStatus || '',
        cardStatus: statuses.cardStatus || '',
        aisUpdateStatus: aisUpdateStatus
      });
      return { success: true, row: rowNumber, aisUpdateStatus: aisUpdateStatus };
    }
  }
  throw new Error('Объект не найден: ' + objectName);
}

function updateAisUpdateStatus(objectName, status) {
  requireAdmin_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(SHEET_STATUS);
  if (!sheet) throw new Error('Лист "' + SHEET_STATUS + '" не найден.');
  ensureAisUpdateColumnWeb_(sheet);

  const normalizedStatus = normalizeAisUpdateStatusWeb_(status);
  const values = sheet.getDataRange().getValues();

  for (let i = 2; i < values.length; i++) {
    const currentObject = String(values[i][0] || '').trim();
    if (normalizeWeb_(currentObject) === normalizeWeb_(objectName)) {
      const rowNumber = i + 1;
      sheet.getRange(rowNumber, AIS_UPDATE_COLUMN).setValue(normalizedStatus);
      logPlatformChange_('monitoring', 'aisUpdateStatus', objectName, {
        objectName: objectName,
        rowNumber: rowNumber,
        aisUpdateStatus: normalizedStatus
      });
      return { success: true, row: rowNumber, aisUpdateStatus: normalizedStatus };
    }
  }

  throw new Error('Объект не найден: ' + objectName);
}

function ensureAisUpdateColumnWeb_(sheet) {
  if (sheet.getMaxColumns() < AIS_UPDATE_COLUMN) {
    sheet.insertColumnsAfter(sheet.getMaxColumns(), AIS_UPDATE_COLUMN - sheet.getMaxColumns());
  }
  const headerRow = 2;
  const headerCell = sheet.getRange(headerRow, AIS_UPDATE_COLUMN);
  if (!String(headerCell.getValue() || '').trim()) {
    headerCell.setValue('Обновление данных в АИС');
  }
}

function normalizeAisUpdateStatusWeb_(value) {
  const s = String(value || '').trim().toLowerCase();
  if (s === 'true' || s === 'да' || s === '1' || s === AIS_UPDATE_DONE.toLowerCase()) return AIS_UPDATE_DONE;
  return AIS_UPDATE_REQUIRED;
}

function isTrueWeb_(value) {
  return String(value || '').trim().toLowerCase() === 'true';
}

function getActsModuleData() {
  requireActiveUser_();
  return {
    objects: getObjectsForSingleAct(),
    files: getActFilesFromDriveMatched_()
  };
}



function getActFilesFromListFast_() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(FILES_LIST_SHEET_NAME);
  if (!sheet || sheet.getLastRow() < 2) return [];

  const lastRow = sheet.getLastRow();
  const lastCol = Math.max(sheet.getLastColumn(), 8);
  const data = sheet.getRange(2, 1, lastRow - 1, lastCol).getDisplayValues();

  // Основная логика ссылок для карточек:
  // B «Наименование файла» = как файл называется на Google Drive;
  // H «Соответствие из листа 1» = наименование объекта.
  // Остальные столбцы не используем как источник ссылки, чтобы не открыть старый/битый URL с 404.
  const driveIndex = buildActsDriveIndexByFileNameWeb_();

  return data.map(r => {
    const fileNameRaw = String(r[1] || '').trim();
    const matchedObject = String(r[7] || '').trim();
    if (!fileNameRaw || !matchedObject) return null;

    const cleanName = stripFileExtensionWeb_(fileNameRaw);
    const found = driveIndex[normalizeObjectNameWeb_(fileNameRaw)] || driveIndex[normalizeObjectNameWeb_(cleanName)];

    return {
      uploadDate: String(r[0] || '').trim(),
      fileName: cleanName,
      mimeType: String(r[2] || '').trim() || 'application/pdf',
      size: String(r[3] || '').trim(),
      recordType: String(r[4] || '').trim() || 'PDF акт',
      archive: String(r[5] || '').trim(),
      fileId: found ? found.id : '',
      url: found ? getDriveViewUrlWeb_(found.id) : '',
      matchedObject: matchedObject
    };
  }).filter(Boolean);
}


function scanDriveFilesRecursiveWeb_(folder, level, maxDepth) {
  const result = [];
  scanDriveFilesRecursiveWebInner_(folder, result, level || 0, maxDepth === undefined ? 10 : maxDepth);
  return result;
}

function scanDriveFilesRecursiveWebInner_(folder, result, level, maxDepth) {
  const files = folder.getFiles();
  while (files.hasNext()) {
    const file = files.next();
    result.push({
      id: file.getId(),
      name: file.getName(),
      url: file.getUrl(),
      mimeType: file.getMimeType(),
      size: file.getSize(),
      folderName: folder.getName(),
      level: level
    });
  }
  if (level >= maxDepth) return;
  const folders = folder.getFolders();
  while (folders.hasNext()) {
    scanDriveFilesRecursiveWebInner_(folders.next(), result, level + 1, maxDepth);
  }
}

function buildActsDriveIndexByFileNameWeb_() {
  const index = {};
  const folder = DriveApp.getFolderById(ACTS_FOLDER_ID);
  scanDriveFilesRecursiveWeb_(folder, 0, 3).forEach(file => {
    const baseKey = normalizeObjectNameWeb_(stripFileExtensionWeb_(file.name));
    const fullKey = normalizeObjectNameWeb_(file.name);
    if (baseKey && !index[baseKey]) index[baseKey] = file;
    if (fullKey && !index[fullKey]) index[fullKey] = file;
  });
  return index;
}

function getDriveViewUrlWeb_(fileId) {
  return fileId ? 'https://drive.google.com/file/d/' + fileId + '/view' : '';
}

function getObjectActOpenUrl(objectName, fileName) {
  requireActiveUser_();
  const targetObject = normalizeWeb_(objectName);
  const targetFile = normalizeObjectNameWeb_(fileName || '');
  const files = getActFilesFromListFast_();
  const found = files.find(f => {
    if (normalizeWeb_(f.matchedObject) !== targetObject) return false;
    if (!targetFile) return true;
    return normalizeObjectNameWeb_(f.fileName) === targetFile || normalizeObjectNameWeb_(f.fileName + '.pdf') === targetFile;
  }) || files.find(f => normalizeWeb_(f.matchedObject) === targetObject);

  if (!found) throw new Error('Для объекта не найден акт в листе «Список_файлов»: ' + objectName);
  if (!found.fileId || !found.url) throw new Error('Файл указан в листе «Список_файлов», но не найден на Google Drive по имени: ' + found.fileName);
  try { DriveApp.getFileById(found.fileId).setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW); } catch (e) {}
  return { success: true, url: getDriveViewUrlWeb_(found.fileId), fileId: found.fileId, fileName: found.fileName, objectName: found.matchedObject };
}

/**
 * Актуальный источник ссылок для сайта: напрямую сканируем папку Google Drive
 * с актами и сопоставляем имена файлов с наименованиями объектов.
 * Лист "Список_файлов" больше не используется как источник ID/URL.
 */
function getActFilesFromDriveMatched_() {
  return getActFilesFromListFast_();
}

function getRichTextLinkWeb_(richTextValue) {
  if (!richTextValue) return '';
  try {
    const direct = richTextValue.getLinkUrl();
    if (direct) return direct;

    const runs = richTextValue.getRuns ? richTextValue.getRuns() : [];
    for (let i = 0; i < runs.length; i++) {
      const link = runs[i].getLinkUrl();
      if (link) return link;
    }
  } catch (e) {}
  return '';
}

function extractDriveFileIdWeb_(value) {
  if (!value) return '';
  const str = String(value).trim();

  let match = str.match(/\/d\/([a-zA-Z0-9_-]{20,})/);
  if (match) return match[1];

  match = str.match(/[?&]id=([a-zA-Z0-9_-]{20,})/);
  if (match) return match[1];

  match = str.match(/[-\w]{25,}/);
  return match ? match[0] : '';
}

function normalizeDriveUrlWeb_(value) {
  if (!value) return '';
  const str = String(value).trim();
  if (!/^https?:\/\//i.test(str)) return '';

  const id = extractDriveFileIdWeb_(str);
  if (id) return getDriveFileUrlWeb_(id) || str;

  return str;
}

function getDriveFileUrlWeb_(fileId) {
  if (!fileId) return '';
  try {
    return DriveApp.getFileById(fileId).getUrl();
  } catch (e) {
    return 'https://drive.google.com/open?id=' + fileId;
  }
}

function findDriveFileByNameInActsFolderWeb_(fileName) {
  if (!fileName) return null;
  const target = normalizeObjectNameWeb_(stripFileExtensionWeb_(fileName));

  try {
    const folder = DriveApp.getFolderById(ACTS_FOLDER_ID);
    const files = folder.getFiles();

    while (files.hasNext()) {
      const file = files.next();
      const current = normalizeObjectNameWeb_(stripFileExtensionWeb_(file.getName()));
      if (current === target) {
        return { id: file.getId(), url: file.getUrl() };
      }
    }
  } catch (e) {}

  return null;
}

function refreshActsLinksFromDrive() {
  requireAdmin_();
  const sheet = SpreadsheetApp.getActive().getSheetByName('Список_файлов');
  const data = sheet.getRange(2, 2, sheet.getLastRow() - 1, 7).getValues();

  // B = имя файла (0 индекс)
  // H = объект (6 индекс)

  const result = data.map(row => {
    const fileName = row[0];
    const objectName = row[6];

    if (!fileName || !objectName) return null;

    const file = findFileByName_(fileName);
    if (!file) return null;

    return {
      fileName: fileName,
      matchedObject: objectName,
      url: "https://drive.google.com/file/d/" + file.getId() + "/view"
    };
  }).filter(Boolean);

  CacheService.getScriptCache().put(
    'ACT_FILES',
    JSON.stringify(result),
    21600
  );

  logPlatformChange_('acts', 'refreshLinks', 'drive', {
    count: result.length
  });
  return { message: 'Акты обновлены: ' + result.length };
}

function syncFilesListSheetFromDriveMatches_(files) {
  requireAdmin_();
  const sheet = getOrCreateFilesListSheet_();
  if (sheet.getLastRow() > 1) {
    sheet.getRange(2, 1, sheet.getLastRow() - 1, Math.max(sheet.getLastColumn(), 8)).clearContent();
  }
  if (!files || !files.length) return;

  const rows = files.map(f => [
    new Date(),
    f.fileName,
    f.mimeType,
    f.size,
    'Файл из папки Google Drive',
    f.archive || '',
    f.url,
    f.matchedObject
  ]);
  sheet.getRange(2, 1, rows.length, 8).setValues(rows);
}

function matchActFilesWithObjects() {
  requireAdmin_();
  const files = getActFilesFromDriveMatched_();
  syncFilesListSheetFromDriveMatches_(files);
  logPlatformChange_('acts', 'matchFiles', 'drive', {
    matched: files.length
  });
  return {
    success: true,
    matched: files.length
  };
}

function createSingleActByObjectName(objectName) {
  requireAdmin_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(SHEET_VOLUMES);
  if (!sheet) throw new Error('Лист "' + SHEET_VOLUMES + '" не найден.');
  const values = sheet.getRange(2, 1, Math.max(sheet.getLastRow() - 1, 0), 1).getDisplayValues();
  for (let i = 0; i < values.length; i++) {
    if (normalizeObjectNameWeb_(values[i][0]) === normalizeObjectNameWeb_(objectName)) {
      const result = createSingleActByRow(i + 2);
      result.url = 'https://docs.google.com/document/d/' + result.docId + '/edit';
      return result;
    }
  }
  throw new Error('Объект не найден на листе "Объемы": ' + objectName);
}


function createMultipleActsByObjectNames(objectNames) {
  requireAdmin_();
  if (!Array.isArray(objectNames) || !objectNames.length) {
    throw new Error('Не выбраны объекты для формирования актов.');
  }

  const seen = {};
  const names = objectNames
    .map(name => String(name || '').trim())
    .filter(Boolean)
    .filter(name => {
      const key = normalizeObjectNameWeb_(name);
      if (!key || seen[key]) return false;
      seen[key] = true;
      return true;
    });

  if (!names.length) {
    throw new Error('Не выбраны объекты для формирования актов.');
  }

  const created = [];
  const errors = [];

  names.forEach(name => {
    try {
      const result = createSingleActByObjectName(name);
      created.push({
        objectName: result.objectName,
        district: result.district,
        actDate: result.actDate,
        docId: result.docId,
        fileName: result.fileName,
        isNew: result.isNew,
        url: result.url || ('https://docs.google.com/document/d/' + result.docId + '/edit')
      });
    } catch (e) {
      errors.push({
        objectName: name,
        message: e && e.message ? e.message : String(e)
      });
    }
  });

  logPlatformChange_('acts', 'createDocsByObjects', names.join(','), {
    total: names.length,
    created: created.length,
    errors: errors.length
  });
  return {
    success: errors.length === 0,
    total: names.length,
    created: created,
    errors: errors
  };
}

function findBestObjectMatchWeb_(fileName, objects) {
  if (!fileName) return '';
  const fileNorm = normalizeObjectNameWeb_(fileName);
  for (const obj of objects) if (normalizeObjectNameWeb_(obj) === fileNorm) return obj;
  for (const obj of objects) {
    const objNorm = normalizeObjectNameWeb_(obj);
    if (objNorm.indexOf(fileNorm) !== -1 || fileNorm.indexOf(objNorm) !== -1) return obj;
  }
  let best = '', bestScore = 0;
  const fileTokens = tokenizeObjectWeb_(fileNorm);
  objects.forEach(obj => {
    const score = calcTokenSimilarityWeb_(fileTokens, tokenizeObjectWeb_(normalizeObjectNameWeb_(obj)));
    if (score > bestScore) { bestScore = score; best = obj; }
  });
  return bestScore >= 0.55 ? best : '';
}

function normalizeObjectNameWeb_(value) {
  let s = String(value || '').toLowerCase().trim();
  s = stripFileExtensionWeb_(s).replace(/^\d+\s*-\s*/g, '');
  s = s.replace(/[«»"']/g, '').replace(/[().,;:]/g, ' ').replace(/\s+/g, ' ').trim();
  const replacements = [[/\bулица\b/g,'ул'],[/\bул\.\b/g,'ул'],[/\bшоссе\b/g,'ш'],[/\bш\.\b/g,'ш'],[/\bпроезд\b/g,'пр'],[/\bпр\.\b/g,'пр'],[/\bпереулок\b/g,'пер'],[/\bпер\.\b/g,'пер'],[/\bбульвар\b/g,'бул'],[/\bбул\.\b/g,'бул'],[/\bпроспект\b/g,'просп'],[/\bпр-т\b/g,'просп'],[/\bплощадь\b/g,'пл'],[/\bпл\.\b/g,'пл'],[/\bнабережная\b/g,'наб'],[/\bнаб\.\b/g,'наб']];
  replacements.forEach(p => s = s.replace(p[0], p[1]));
  return s.replace(/\s+/g, ' ').trim();
}
function tokenizeObjectWeb_(value) { return String(value || '').split(' ').map(x => x.trim()).filter(Boolean); }
function calcTokenSimilarityWeb_(a, b) { if (!a.length || !b.length) return 0; const setB = {}; b.forEach(t => setB[t] = true); let common = 0; a.forEach(t => { if (setB[t]) common++; }); return common / Math.max(a.length, b.length); }
function stripFileExtensionWeb_(fileName) { return String(fileName || '').replace(/\.[^.]+$/, '').trim(); }
function formatBytesWeb_(bytes) { if (!bytes || bytes <= 0) return '0 Б'; const units = ['Б','КБ','МБ','ГБ']; let size = Number(bytes), i = 0; while (size >= 1024 && i < units.length - 1) { size /= 1024; i++; } return (size >= 10 || i === 0 ? size.toFixed(0) : size.toFixed(2)) + ' ' + units[i]; }
function formatDateWeb_(value) { if (!value) return ''; if (Object.prototype.toString.call(value) === '[object Date]') return Utilities.formatDate(value, Session.getScriptTimeZone(), 'dd.MM.yyyy'); return String(value).trim(); }
function numWeb_(value) { if (value === '' || value === null || value === undefined) return 0; const n = Number(String(value).replace(',', '.')); return isNaN(n) ? 0 : n; }
function normalizeWeb_(value) { return String(value || '').toLowerCase().replace(/[«»]/g, '"').replace(/\s+/g, ' ').trim(); }


/*************** МЕНЮ ***************/
function onOpen() {
  const ui = SpreadsheetApp.getUi();

  ui.createMenu('Формирование актов')
    .addSubMenu(
      ui.createMenu('Акты')
        .addItem('Создать Google Docs', 'startCreateDocs')
        .addItem('Продолжить создание Google Docs', 'processCreateDocsBatch')
        .addSeparator()
        .addItem('Начать экспорт в PDF', 'startExportPdf')
        .addItem('Продолжить экспорт в PDF', 'processExportPdfBatch')
        .addSeparator()
        .addItem('Сформировать акт по объекту', 'showSingleActDialog')
        .addSeparator()
        .addItem('Создать тестовый документ', 'testCreateOneDoc')
    )
    .addSubMenu(
      ui.createMenu('Файлы')
        .addItem('Загрузить файлы', 'showFileUploadSidebar')
        .addItem('Сканировать папку Drive', 'runScanUploadsFolderFromMenu')
        .addItem('Очистить список файлов', 'clearFilesListSheet')
        .addSeparator()
        .addItem('Сопоставить с листом 1', 'matchFilesListWithFirstSheet')
    )
     .addSubMenu(
      ui.createMenu('Страницы PDF')
        .addItem('Экспортировать страницы PDF', 'startExportPdfPageCounts')
        .addItem('Продолжить экспорт страниц PDF', 'processExportPdfPageCountsBatch')
        .addItem('Сбросить экспорт страниц PDF', 'resetPdfPageCountsProgress')
        .addSeparator()
        .addItem('Переименовать PDF по листу "Список_файлов"', 'renamePdfFilesByFilesList')
     )
    .addSubMenu(
      ui.createMenu('Сервис')
        .addItem('Сбросить прогресс', 'resetAllProgress')
    )
    .addToUi();
}

/*************** ЭТАП 1 ***************/
function startCreateDocs() {
  deleteExistingTriggers_('processCreateDocsBatch');
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty('create_last_index');
  props.deleteProperty('create_count');
  props.deleteProperty('create_skipped_no_date');
  props.deleteProperty('create_skipped_existing');
  processCreateDocsBatch();
}

function processCreateDocsBatch() {
  deleteExistingTriggers_('processCreateDocsBatch');

  const props = PropertiesService.getScriptProperties();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = SHEET_NAME ? ss.getSheetByName(SHEET_NAME) : ss.getSheets()[0];
  if (!sheet) throw new Error('Лист не найден.');

  const values = sheet.getDataRange().getDisplayValues();
  if (values.length < 2) throw new Error('Нет данных.');

  const dataRows = values.slice(1).filter(row => String(row[0]).trim() !== '');
  const folders = getWorkFolders_();
  const docsFolder = folders.docsFolder;

  let startIndex = Number(props.getProperty('create_last_index') || '0');
  let createdCount = Number(props.getProperty('create_count') || '0');
  let skippedNoDate = Number(props.getProperty('create_skipped_no_date') || '0');
  let skippedExisting = Number(props.getProperty('create_skipped_existing') || '0');

  const endIndex = Math.min(startIndex + CREATE_BATCH_SIZE, dataRows.length);

  for (let i = startIndex; i < endIndex; i++) {
    const row = dataRows[i];

    try {
      const objectName = safeCell_(row, 0);
      const district = safeCell_(row, 1);
      const actDateRaw = safeCell_(row, SHEET_DATE_COL);

      // Пустая дата в N — пропускаем
      if (!actDateRaw) {
        skippedNoDate++;
        Logger.log('Строка ' + (i + 2) + ': пропущена, пустой столбец N');
        continue;
      }

      const actDate = formatActDateRu_(actDateRaw);

      // Некорректная дата — пропускаем
      if (!actDate) {
        skippedNoDate++;
        Logger.log('Строка ' + (i + 2) + ': пропущена, некорректная дата в N: ' + actDateRaw);
        continue;
      }

      const workValues = row.slice(SHEET_WORK_START_COL, SHEET_WORK_END_COL + 1);
      const fileName = sanitizeFileName_((i + 1) + ' - ' + objectName);

      const result = createDocFromTemplate_({
        templateDocId: TEMPLATE_DOC_ID,
        outputFolder: docsFolder,
        fileName,
        objectName,
        district,
        actDate,
        workValues
      });

      if (result.isNew) {
        createdCount++;
      } else {
        skippedExisting++;
      }

    } catch (e) {
      logError_('Создание Google Docs', i + 2, e.message);
    }
  }

  props.setProperty('create_last_index', String(endIndex));
  props.setProperty('create_count', String(createdCount));
  props.setProperty('create_skipped_no_date', String(skippedNoDate));
  props.setProperty('create_skipped_existing', String(skippedExisting));

  if (endIndex < dataRows.length) {
    ScriptApp.newTrigger('processCreateDocsBatch').timeBased().after(10000).create();
    SpreadsheetApp.getActive().toast(
      'Создание Google Docs: ' + endIndex + ' из ' + dataRows.length,
      'Формирование актов',
      10
    );
  } else {
    deleteExistingTriggers_('processCreateDocsBatch');
    SpreadsheetApp.getUi().alert(
      'Этап 1 завершён.\n' +
      'Новых Google Docs создано: ' + createdCount + '\n' +
      'Пропущено без даты: ' + skippedNoDate + '\n' +
      'Пропущено, т.к. файл уже существовал: ' + skippedExisting + '\n' +
      'Теперь запусти экспорт в PDF.'
    );
  }
}

function replaceWorksBlockTitle_(docId) {
  const doc = DocumentApp.openById(docId);
  const body = doc.getBody();

  const textToInsert =
    '1. Комиссия, в дополнение к ранее рассмотренным документам, подтверждает следующие выполненные объемы работ:';

  const found = body.findText('{{WORKS_BLOCK_TITLE}}');

  if (!found) return;

  const element = found.getElement().asText();
  const start = found.getStartOffset();
  const end = found.getEndOffsetInclusive();

  // Заменяем текст
  element.deleteText(start, end);
  element.insertText(start, textToInsert);

  // Применяем стиль ко всей вставленной строке
  element.setFontFamily(start, start + textToInsert.length - 1, 'Times New Roman');
  element.setFontSize(start, start + textToInsert.length - 1, 12);
  element.setBold(start, start + textToInsert.length - 1, true);
}

/*************** ТЕСТ ***************/
function testCreateOneDoc() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = SHEET_NAME ? ss.getSheetByName(SHEET_NAME) : ss.getSheets()[0];
  if (!sheet) throw new Error('Лист не найден.');

  const values = sheet.getDataRange().getDisplayValues();
  if (values.length < 2) throw new Error('Нет данных.');

  const dataRows = values.slice(1).filter(row => String(row[0]).trim() !== '');
  if (!dataRows.length) throw new Error('Нет строк с данными.');

  const row = dataRows[0];
  const objectName = safeCell_(row, 0);
  const district = safeCell_(row, 1);
  const actDateRaw = safeCell_(row, SHEET_DATE_COL);

  if (!actDateRaw) {
    throw new Error('В столбце N нет даты. Тестовый документ не создан.');
  }

  const actDate = formatActDateRu_(actDateRaw);

  if (!actDate) {
    throw new Error('Дата в столбце N имеет некорректный формат: ' + actDateRaw);
  }

  const workValues = row.slice(SHEET_WORK_START_COL, SHEET_WORK_END_COL + 1);

  const folders = getWorkFolders_();
  const fileName = sanitizeFileName_('TEST - ' + objectName);

  const docId = createDocFromTemplate_({
    templateDocId: TEMPLATE_DOC_ID,
    outputFolder: folders.docsFolder,
    fileName,
    objectName,
    district,
    actDate,
    workValues
  });

  SpreadsheetApp.getUi().alert('Тестовый документ создан.\nID: ' + docId);
}

/*************** ЭТАП 2 ***************/
function startExportPdf() {
  deleteExistingTriggers_('processExportPdfBatch');
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty('export_last_index');
  props.deleteProperty('export_count');
  props.deleteProperty('export_skipped_existing');
  processExportPdfBatch();
}

function processExportPdfBatch() {
  deleteExistingTriggers_('processExportPdfBatch');

  const props = PropertiesService.getScriptProperties();
  const folders = getWorkFolders_();
  const docsFolder = folders.docsFolder;
  const pdfFolder = folders.pdfFolder;

  const files = [];
  const iter = docsFolder.getFiles();

  while (iter.hasNext()) {
    const file = iter.next();
    if (file.getMimeType() === MimeType.GOOGLE_DOCS) {
      files.push(file);
    }
  }

  files.sort((a, b) => a.getName().localeCompare(b.getName(), 'ru'));

  let startIndex = Number(props.getProperty('export_last_index') || '0');
  let exportedCount = Number(props.getProperty('export_count') || '0');
  let skippedExisting = Number(props.getProperty('export_skipped_existing') || '0');

  const endIndex = Math.min(startIndex + EXPORT_BATCH_SIZE, files.length);

  for (let i = startIndex; i < endIndex; i++) {
    const file = files[i];
    try {
      const fileName = file.getName() + '.pdf';

      const existingPdf = findFileByName_(pdfFolder, fileName);
      if (existingPdf) {
        skippedExisting++;
        continue;
      }

      exportGoogleDocToPdf_(file.getId(), pdfFolder, fileName);
      exportedCount++;
    } catch (e) {
      logError_('Экспорт PDF', i + 1, file.getName() + ': ' + e.message);
    }
  }

  props.setProperty('export_last_index', String(endIndex));
  props.setProperty('export_count', String(exportedCount));
  props.setProperty('export_skipped_existing', String(skippedExisting));

  if (endIndex < files.length) {
    ScriptApp.newTrigger('processExportPdfBatch').timeBased().after(10000).create();
    SpreadsheetApp.getActive().toast(
      'Экспорт PDF: ' + endIndex + ' из ' + files.length,
      'Формирование актов',
      10
    );
  } else {
    deleteExistingTriggers_('processExportPdfBatch');
    SpreadsheetApp.getUi().alert(
      'Этап 2 завершён.\n' +
      'Новых PDF экспортировано: ' + exportedCount + '\n' +
      'Пропущено, т.к. PDF уже существовал: ' + skippedExisting
    );
  }
}

/*************** СОЗДАНИЕ ДОКУМЕНТА ***************/
function createDocFromTemplate_(params) {
  const {
    templateDocId,
    outputFolder,
    fileName,
    objectName,
    district,
    actDate,
    workValues
  } = params;

  const existing = findFileByName_(outputFolder, fileName, MimeType.GOOGLE_DOCS);
  if (existing) {
    return {
      docId: existing.getId(),
      isNew: false
    };
  }

  const templateFile = DriveApp.getFileById(templateDocId);
  const copiedFile = templateFile.makeCopy(fileName, outputFolder);
  const docId = copiedFile.getId();

  replacePlaceholdersViaDocsApi_(docId, {
    '(Наименование объекта)': objectName,
    '(Округ)': district,
    '{{ACT_DATE}}': actDate
  });

  // 👉 Вставка текста комиссии через плейсхолдер
  replaceWorksBlockTitle_(docId);

  const doc = DocumentApp.openById(docId);
  const body = doc.getBody();

  fillTableByPosition_(body, workValues);

  doc.saveAndClose();

  return {
    docId: docId,
    isNew: true
  };
}

function ensureCommissionParagraphAboveTable_(body) {
  if (!body) return;

  let firstTableIndex = -1;
  let commissionParagraph = null;
  let commissionIndex = -1;

  for (let i = 0; i < body.getNumChildren(); i++) {
    const child = body.getChild(i);
    const type = child.getType();

    if (firstTableIndex === -1 && type === DocumentApp.ElementType.TABLE) {
      firstTableIndex = i;
    }

    if (type === DocumentApp.ElementType.PARAGRAPH) {
      const p = child.asParagraph();
      const text = normalizeDocText_(p.getText());

      if (text.indexOf('1. Комиссия') === 0) {
        commissionParagraph = p;
        commissionIndex = i;
      }
    }
  }

  if (firstTableIndex === -1 || !commissionParagraph) {
    return;
  }

  // Уже стоит прямо перед таблицей
  if (commissionIndex === firstTableIndex - 1) {
    return;
  }

  const paragraphText = commissionParagraph.getText();
  const paragraphAttrs = commissionParagraph.getAttributes();

  // Вставляем абзац перед таблицей
  const insertedParagraph = body.insertParagraph(firstTableIndex, paragraphText);
  insertedParagraph.setAttributes(paragraphAttrs);

  // Если исходный абзац был после таблицы, после вставки его индекс сдвигается на +1
  const oldParagraphIndexToRemove =
    commissionIndex >= firstTableIndex ? commissionIndex + 1 : commissionIndex;

  body.removeChild(body.getChild(oldParagraphIndexToRemove));
}

function normalizeDocText_(text) {
  return String(text || '')
    .replace(/\s+/g, ' ')
    .trim();
}

/*************** ЗАМЕНА ПЛЕЙСХОЛДЕРОВ ***************/
function replacePlaceholdersViaDocsApi_(docId, replacements) {
  // Раньше здесь использовался Advanced Google Service `Docs.Documents.batchUpdate`,
  // из-за чего сайт падал с ошибкой `ReferenceError: Docs is not defined`,
  // если Google Docs API не был подключен в сервисах Apps Script.
  // Для обычной замены плейсхолдеров достаточно стандартного DocumentApp.
  const doc = DocumentApp.openById(docId);
  const body = doc.getBody();

  Object.keys(replacements || {}).forEach(key => {
    body.replaceText(escapeRegExpForDocumentApp_(key), String(replacements[key] || ''));
  });

  doc.saveAndClose();
}

function escapeRegExpForDocumentApp_(text) {
  return String(text || '').replace(/[\\^$.*+?()[\]{}|]/g, '\\$&');
}

/*************** ЗАПОЛНЕНИЕ ТАБЛИЦЫ ***************/
function fillTableByPosition_(body, workValues) {
  const tables = body.getTables();
  if (!tables.length) throw new Error('В шаблоне нет таблиц.');
  if (TEMPLATE_TABLE_INDEX >= tables.length) {
    throw new Error('Таблица с индексом ' + TEMPLATE_TABLE_INDEX + ' не найдена.');
  }

  const table = tables[TEMPLATE_TABLE_INDEX];

  for (let i = workValues.length - 1; i >= 0; i--) {
    const tableRowIndex = TABLE_DATA_START_ROW + i;

    if (tableRowIndex >= table.getNumRows()) {
      throw new Error('В таблице шаблона меньше строк, чем ожидается.');
    }

    const rawValue = workValues[i];
    const row = table.getRow(tableRowIndex);

    if (row.getNumCells() <= DOC_COL_FACT) {
      throw new Error('В строке таблицы недостаточно колонок.');
    }

    if (isZeroLike_(rawValue)) {
      table.removeRow(tableRowIndex);
      continue;
    }

    const value = normalizeOutputValue_(rawValue);
    row.getCell(DOC_COL_PLAN).setText(value);
    row.getCell(DOC_COL_FACT).setText(value);
  }

  let counter = 1;

  for (let r = TABLE_DATA_START_ROW; r < table.getNumRows(); r++) {
    const row = table.getRow(r);
    if (row.getNumCells() === 0) continue;
    row.getCell(0).setText(String(counter));
    counter++;
  }
}

function isZeroLike_(value) {
  const s = String(value == null ? '' : value)
    .replace(/\u00A0/g, ' ')
    .trim();

  if (s === '') return true;

  const normalized = s
    .replace(/\s+/g, '')
    .replace(',', '.');

  if (!/^[-+]?\d*\.?\d+$/.test(normalized)) {
    return false;
  }

  return Number(normalized) === 0;
}

function normalizeOutputValue_(value) {
  return String(value == null ? '' : value).trim();
}

/*************** ФОРМАТ ДАТЫ ***************/
function formatActDateRu_(value) {
  const months = {
    '01': 'января',
    '02': 'февраля',
    '03': 'марта',
    '04': 'апреля',
    '05': 'мая',
    '06': 'июня',
    '07': 'июля',
    '08': 'августа',
    '09': 'сентября',
    '10': 'октября',
    '11': 'ноября',
    '12': 'декабря'
  };

  let s = String(value == null ? '' : value).trim();
  if (!s) return '';

  s = s.replace(/\s+/g, '');

  const match = s.match(/^(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?$/);
  if (!match) return s;

  const day = ('0' + match[1]).slice(-2);
  const monthNum = ('0' + match[2]).slice(-2);
  const monthText = months[monthNum];

  if (!monthText) return s;

  return '«' + day + '» ' + monthText;
}


/**
 * Точное формирование актов по выбранным строкам листа «Объемы».
 * Используется для сайта вместо поиска по названию объекта, чтобы объекты
 * с похожими наименованиями вроде «1-я/2-я/3-я ... улица» не подменялись.
 */
function createMultipleActsByRowNumbers(rowNumbers) {
  requireAdmin_();
  const rows = normalizeSelectedActRows_(rowNumbers);
  if (!rows.length) {
    throw new Error('Не выбраны объекты для формирования актов.');
  }

  const created = [];
  const errors = [];

  rows.forEach(rowNumber => {
    try {
      const result = createSingleActByRow(rowNumber);
      created.push({
        rowNumber: rowNumber,
        objectName: result.objectName,
        district: result.district,
        actDate: result.actDate,
        docId: result.docId,
        fileName: result.fileName,
        isNew: result.isNew,
        url: 'https://docs.google.com/document/d/' + result.docId + '/edit'
      });
    } catch (e) {
      errors.push({
        rowNumber: rowNumber,
        objectName: 'Строка ' + rowNumber,
        message: e && e.message ? e.message : String(e)
      });
    }
  });

  logPlatformChange_('acts', 'createDocsByRows', rows.join(','), {
    total: rows.length,
    created: created.length,
    errors: errors.length
  });
  return {
    success: errors.length === 0,
    total: rows.length,
    created: created,
    errors: errors
  };
}

function normalizeSelectedActRows_(rowNumbers) {
  if (!Array.isArray(rowNumbers)) return [];
  const seen = {};
  return rowNumbers
    .map(v => Number(v))
    .filter(n => Number.isFinite(n) && n >= 2)
    .filter(n => {
      const key = String(n);
      if (seen[key]) return false;
      seen[key] = true;
      return true;
    });
}

/*************** ТОЧЕЧНОЕ ФОРМИРОВАНИЕ АКТА ***************/
function showSingleActDialog() {
  const html = HtmlService.createHtmlOutputFromFile('SingleActDialog')
    .setWidth(520)
    .setHeight(420);
  SpreadsheetApp.getUi().showModalDialog(html, 'Сформировать акт по объекту');
}

function getObjectsForSingleAct() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = SHEET_NAME ? ss.getSheetByName(SHEET_NAME) : ss.getSheets()[0];
  if (!sheet) throw new Error('Лист не найден.');

  const lastRow = sheet.getLastRow();
  const lastCol = Math.max(sheet.getLastColumn(), 14);

  if (lastRow < 2) return [];

  const values = sheet.getRange(2, 1, lastRow - 1, lastCol).getDisplayValues();
  const result = [];

  for (let i = 0; i < values.length; i++) {
    const row = values[i];

    const objectName = String(row[0] || '').trim(); // A
    const district = String(row[1] || '').trim();   // B
    const actDateRaw = String(row[13] || '').trim(); // N

    // Показываем только объекты, у которых есть дата в N
    if (!objectName || !actDateRaw) continue;

    result.push({
      rowNumber: i + 2,
      objectName: objectName,
      district: district,
      actDateRaw: actDateRaw,
      label: district ? (objectName + ' (' + district + ')') : objectName
    });
  }

  result.sort((a, b) => a.label.localeCompare(b.label, 'ru'));

  Logger.log('getObjectsForSingleAct(): найдено объектов = ' + result.length);
  return result;
}

function createSingleActByRow(rowNumber) {
  requireAdmin_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = SHEET_NAME ? ss.getSheetByName(SHEET_NAME) : ss.getSheets()[0];
  if (!sheet) throw new Error('Лист не найден.');

  const lastCol = Math.max(sheet.getLastColumn(), 14);
  const row = sheet.getRange(rowNumber, 1, 1, lastCol).getDisplayValues()[0];

  const objectName = String(row[0] || '').trim();   // A
  const district = String(row[1] || '').trim();     // B
  const actDateRaw = String(row[13] || '').trim();  // N

  if (!objectName) {
    throw new Error('В выбранной строке отсутствует наименование объекта.');
  }

  if (!actDateRaw) {
    throw new Error('В столбце N отсутствует дата. Акт не создан.');
  }

  const actDate = formatActDateRu_(actDateRaw);
  if (!actDate) {
    throw new Error('Некорректная дата в столбце N: ' + actDateRaw);
  }

  const workValues = row.slice(SHEET_WORK_START_COL, SHEET_WORK_END_COL + 1);
  const folders = getWorkFolders_();
  const docsFolder = folders.docsFolder;

  const fileName = sanitizeFileName_('Точечно - ' + objectName);

  const result = createDocFromTemplate_({
    templateDocId: TEMPLATE_DOC_ID,
    outputFolder: docsFolder,
    fileName,
    objectName,
    district,
    actDate,
    workValues
  });

  return {
    success: true,
    objectName: objectName,
    district: district,
    actDate: actDate,
    docId: result.docId,
    isNew: result.isNew,
    fileName: fileName
  };
}

function createSingleActByRow(rowNumber) {
  requireAdmin_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = SHEET_NAME ? ss.getSheetByName(SHEET_NAME) : ss.getSheets()[0];
  if (!sheet) throw new Error('Лист не найден.');

  const lastCol = Math.max(sheet.getLastColumn(), 14);
  const row = sheet.getRange(rowNumber, 1, 1, lastCol).getDisplayValues()[0];

  const objectName = safeCell_(row, 0);   // A
  const district   = safeCell_(row, 1);   // B
  const actDateRaw = safeCell_(row, 13);  // N

  if (!objectName) {
    throw new Error('В выбранной строке отсутствует наименование объекта.');
  }

  if (!actDateRaw) {
    throw new Error('В столбце N отсутствует дата. Акт не создан.');
  }

  const actDate = formatActDateRu_(actDateRaw);
  if (!actDate) {
    throw new Error('Некорректная дата в столбце N: ' + actDateRaw);
  }

  const workValues = row.slice(SHEET_WORK_START_COL, SHEET_WORK_END_COL + 1);
  const folders = getWorkFolders_();
  const docsFolder = folders.docsFolder;

  const fileName = sanitizeFileName_('Точечно - ' + objectName);

  const result = createDocFromTemplate_({
    templateDocId: TEMPLATE_DOC_ID,
    outputFolder: docsFolder,
    fileName,
    objectName,
    district,
    actDate,
    workValues
  });

  return {
    success: true,
    objectName: objectName,
    district: district,
    actDate: actDate,
    docId: result.docId,
    isNew: result.isNew,
    fileName: fileName
  };
}

/*************** ЭКСПОРТ ***************/
function exportGoogleDocToPdf_(docId, folder, fileName) {
  const url = 'https://www.googleapis.com/drive/v3/files/' + docId +
    '/export?mimeType=' +
    encodeURIComponent('application/pdf');

  const response = UrlFetchApp.fetch(url, {
    headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() },
    muteHttpExceptions: true
  });

  if (response.getResponseCode() !== 200) {
    throw new Error('Ошибка экспорта PDF. Код: ' + response.getResponseCode());
  }

  const blob = response.getBlob().setName(fileName);
  return folder.createFile(blob).getId();
}

function createMultipleActsPdfByObjectNames(objectNames) {
  requireAdmin_();
  if (!Array.isArray(objectNames) || !objectNames.length) {
    throw new Error('Не выбраны объекты для формирования PDF-актов.');
  }

  const seen = {};
  const names = objectNames
    .map(name => String(name || '').trim())
    .filter(Boolean)
    .filter(name => {
      const key = normalizeObjectNameWeb_(name);
      if (!key || seen[key]) return false;
      seen[key] = true;
      return true;
    });

  if (!names.length) {
    throw new Error('Не выбраны объекты для формирования PDF-актов.');
  }

  const pdfFolder = getWorkFolders_().pdfFolder;
  const created = [];
  const errors = [];

  names.forEach(name => {
    try {
      const docResult = createSingleActByObjectName(name);
      const pdfFileName = ensurePdfExtension_(docResult.fileName);
      let pdfFile = findFileByName_(pdfFolder, pdfFileName, MimeType.PDF);
      let isNewPdf = false;

      if (!pdfFile) {
        const pdfId = exportGoogleDocToPdf_(docResult.docId, pdfFolder, pdfFileName);
        pdfFile = DriveApp.getFileById(pdfId);
        isNewPdf = true;
      }

      created.push({
        objectName: docResult.objectName,
        district: docResult.district,
        actDate: docResult.actDate,
        docId: docResult.docId,
        pdfId: pdfFile.getId(),
        fileName: pdfFileName,
        isNewDoc: docResult.isNew,
        isNewPdf: isNewPdf,
        url: pdfFile.getUrl(),
        docUrl: docResult.url || ('https://docs.google.com/document/d/' + docResult.docId + '/edit')
      });
    } catch (e) {
      errors.push({
        objectName: name,
        message: e && e.message ? e.message : String(e)
      });
    }
  });

  logPlatformChange_('acts', 'createPdfByObjects', names.join(','), {
    total: names.length,
    created: created.length,
    errors: errors.length
  });
  return {
    success: errors.length === 0,
    total: names.length,
    created: created,
    errors: errors
  };
}


/**
 * Точный экспорт PDF по выбранным строкам листа «Объемы».
 * Не ищет строку по названию, поэтому не путает похожие объекты.
 */
function createMultipleActsPdfByRowNumbers(rowNumbers) {
  requireAdmin_();
  const rows = normalizeSelectedActRows_(rowNumbers);
  if (!rows.length) {
    throw new Error('Не выбраны объекты для формирования PDF-актов.');
  }

  const pdfFolder = getWorkFolders_().pdfFolder;
  const created = [];
  const errors = [];

  rows.forEach(rowNumber => {
    try {
      const docResult = createSingleActByRow(rowNumber);
      const pdfFileName = ensurePdfExtension_(docResult.fileName);
      let pdfFile = findFileByName_(pdfFolder, pdfFileName, MimeType.PDF);
      let isNewPdf = false;

      if (!pdfFile) {
        const pdfId = exportGoogleDocToPdf_(docResult.docId, pdfFolder, pdfFileName);
        pdfFile = DriveApp.getFileById(pdfId);
        isNewPdf = true;
      }

      created.push({
        rowNumber: rowNumber,
        objectName: docResult.objectName,
        district: docResult.district,
        actDate: docResult.actDate,
        docId: docResult.docId,
        pdfId: pdfFile.getId(),
        fileName: pdfFileName,
        isNewDoc: docResult.isNew,
        isNewPdf: isNewPdf,
        url: pdfFile.getUrl(),
        docUrl: 'https://docs.google.com/document/d/' + docResult.docId + '/edit'
      });
    } catch (e) {
      errors.push({
        rowNumber: rowNumber,
        objectName: 'Строка ' + rowNumber,
        message: e && e.message ? e.message : String(e)
      });
    }
  });

  logPlatformChange_('acts', 'createPdfByRows', rows.join(','), {
    total: rows.length,
    created: created.length,
    errors: errors.length
  });
  return {
    success: errors.length === 0,
    total: rows.length,
    created: created,
    errors: errors
  };
}

function ensurePdfExtension_(fileName) {
  const value = String(fileName || '').trim();
  return /\.pdf$/i.test(value) ? value : value + '.pdf';
}

/*************** ЗАГРУЗКА ФАЙЛОВ И СПИСОК ***************/
function showFileUploadSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('UploadFiles')
    .setTitle('Загрузка файлов');
  SpreadsheetApp.getUi().showSidebar(html);
}

function uploadFilesFromSidebar(files) {
  requireAdmin_();
  if (!files || !files.length) {
    throw new Error('Файлы не переданы.');
  }

  const uploadsFolder = getOrCreateFolder_(UPLOADS_FOLDER_NAME);
  const sheet = getOrCreateFilesListSheet_();
  const rowsBuffer = [];
  let uploadedCount = 0;

  files.forEach(file => {
    if (!file || !file.bytes || !file.name) return;

    const contentType = file.mimeType || 'application/octet-stream';
    const bytes = Utilities.base64Decode(file.bytes);
    const blob = Utilities.newBlob(bytes, contentType, file.name);
    const savedFile = uploadsFolder.createFile(blob);

    const originalFileName = file.name;
    const displayFileName = stripFileExtension_(originalFileName);
    const fileId = savedFile.getId();
    const fileSize = blob.getBytes().length;
    const lowerName = String(originalFileName).toLowerCase();
    const isZip = lowerName.endsWith('.zip') || contentType === 'application/zip';

    rowsBuffer.push([
      new Date(),
      displayFileName,
      contentType,
      formatBytes_(fileSize),
      'Загруженный файл',
      '',
      fileId,
      ''
    ]);

    uploadedCount++;

    if (isZip) {
      if (fileSize > MAX_UNZIP_SIZE_BYTES) {
        rowsBuffer.push([
          new Date(),
          '',
          '',
          '',
          'ZIP слишком большой для распаковки',
          displayFileName,
          fileId,
          ''
        ]);
      } else {
        try {
          const unzippedBlobs = Utilities.unzip(blob);

          if (unzippedBlobs && unzippedBlobs.length) {
            unzippedBlobs.forEach(innerBlob => {
              rowsBuffer.push([
                new Date(),
                '',
                '',
                '',
                'ZIP слишком большой для распаковки',
                displayFileName,
                fileId,
                ''
              ]);
            });
          } else {
            rowsBuffer.push([
              new Date(),
              '',
              '',
              '',
              'ZIP без распознанных вложений',
              displayFileName,
              fileId,
              ''
            ]);
          }
        } catch (e) {
          rowsBuffer.push([
            new Date(),
            '',
            '',
            '',
            'Ошибка чтения ZIP: ' + e.message,
            displayFileName,
            fileId,
            ''
          ]);
        }
      }
    }
  });

  appendRowsBulk_(sheet, rowsBuffer);
  formatFilesListSheet_();

  return {
    success: true,
    uploadedCount: uploadedCount,
    message:
      'Файлы загружены.\n' +
      'Обработано: ' + uploadedCount + '\n' +
      'Список обновлен на листе "' + FILES_LIST_SHEET_NAME + '".'
  };
}

function runScanUploadsFolderFromMenu() {
  const result = scanUploadsFolderAndListFilesTurbo_();
  SpreadsheetApp.getUi().alert(result.message || 'Готово.');
}

function scanUploadsFolderAndListFiles() {
  requireAdmin_();
  return scanUploadsFolderAndListFilesTurbo_();
}

function scanUploadsFolderAndListFilesTurbo_() {
  const uploadsFolder = getOrCreateFolder_(UPLOADS_FOLDER_NAME);
  const sheet = getOrCreateFilesListSheet_();

  const iter = uploadsFolder.getFiles();
  const rowsBuffer = [];
  let processed = 0;
  let zipProcessed = 0;
  let zipSkippedLarge = 0;

  while (iter.hasNext()) {
    const file = iter.next();
    const originalFileName = file.getName();
    const displayFileName = stripFileExtension_(originalFileName);
    const contentType = file.getMimeType() || 'application/octet-stream';
    const fileSize = Number(file.getSize() || 0);
    const fileId = file.getId();
    const lowerName = String(originalFileName).toLowerCase();
    const isZip = lowerName.endsWith('.zip') || contentType === 'application/zip';

   rowsBuffer.push([
      new Date(),
      displayFileName,
      contentType,
      formatBytes_(fileSize),
      'Файл из папки Drive',
      '',
      fileId,
      ''
    ]);

    processed++;

    if (isZip) {
      if (fileSize > MAX_UNZIP_SIZE_BYTES) {
        rowsBuffer.push([
          new Date(),
          '',
          '',
          '',
          'ZIP слишком большой для распаковки',
          displayFileName,
          fileId,
          ''
        ]);
        zipSkippedLarge++;
      } else {
        try {
          const blob = file.getBlob();
          const unzippedBlobs = Utilities.unzip(blob);

          if (unzippedBlobs && unzippedBlobs.length) {
            for (let i = 0; i < unzippedBlobs.length; i++) {
              const innerBlob = unzippedBlobs[i];
              rowsBuffer.push([
                new Date(),
                stripFileExtension_(innerBlob.getName()),
                innerBlob.getContentType() || '',
                formatBytes_(innerBlob.getBytes().length),
                'Файл внутри ZIP',
                displayFileName,
                fileId,
                ''
              ]);
            }
          } else {
            rowsBuffer.push([
              new Date(),
              '',
              '',
              '',
              'ZIP без распознанных вложений',
              displayFileName,
              fileId,
              ''
            ]);
          }

          zipProcessed++;
        } catch (e) {
          rowsBuffer.push([
            new Date(),
            '',
            '',
            '',
            'Ошибка чтения ZIP: ' + e.message,
            displayFileName,
            fileId,
            ''
          ]);
        }
      }
    }

    if (rowsBuffer.length >= DRIVE_SCAN_BATCH_WRITE) {
      appendRowsBulk_(sheet, rowsBuffer);
      rowsBuffer.length = 0;
    }
  }

  if (rowsBuffer.length) {
    appendRowsBulk_(sheet, rowsBuffer);
  }

  formatFilesListSheet_();

  return {
    success: true,
    message:
      'Обработано файлов: ' + processed + '\n' +
      'Распаковано ZIP: ' + zipProcessed + '\n' +
      'Пропущено больших ZIP: ' + zipSkippedLarge + '\n' +
      'Список обновлен на листе "' + FILES_LIST_SHEET_NAME + '".'
  };
}

function appendRowsBulk_(sheet, rows) {
  if (!rows || !rows.length) return;

  const startRow = sheet.getLastRow() + 1;
  const numRows = rows.length;
  const numCols = rows[0].length;

  sheet.getRange(startRow, 1, numRows, numCols).setValues(rows);
}

function getOrCreateFilesListSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(FILES_LIST_SHEET_NAME);

  const headers = [[
    'Дата загрузки',
    'Наименование файла',
    'MIME type',
    'Размер',
    'Тип записи',
    'Архив',
    'ID файла в Drive',
    'Соответствие из листа 1'
  ]];

  if (!sheet) {
    sheet = ss.insertSheet(FILES_LIST_SHEET_NAME);
    sheet.getRange(1, 1, 1, headers[0].length).setValues(headers);
    sheet.setFrozenRows(1);
  } else {
    const currentLastCol = Math.max(sheet.getLastColumn(), 1);
    const currentHeaders = sheet.getRange(1, 1, 1, currentLastCol).getValues()[0];
    if (currentHeaders.length < 8 || currentHeaders[7] !== 'Соответствие из листа 1') {
      sheet.getRange(1, 1, 1, headers[0].length).setValues(headers);
    }
  }

  return sheet;
}

function clearFilesListSheet() {
  requireAdmin_();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(FILES_LIST_SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(FILES_LIST_SHEET_NAME);
  }

  sheet.clear();

  sheet.getRange(1, 1, 1, 8).setValues([[
    'Дата загрузки',
    'Наименование файла',
    'MIME type',
    'Размер',
    'Тип записи',
    'Архив',
    'ID файла в Drive',
    'Соответствие из листа 1'
  ]]);

  sheet.setFrozenRows(1);
  formatFilesListSheet_();

  SpreadsheetApp.getUi().alert('Лист списка файлов очищен.');
}

function formatFilesListSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(FILES_LIST_SHEET_NAME);
  if (!sheet) return;

  const lastRow = Math.max(sheet.getLastRow(), 1);
  const lastCol = 8;

  sheet.getRange(1, 1, 1, lastCol)
    .setFontWeight('bold')
    .setBackground('#d9ead3');

  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, lastCol).setVerticalAlignment('middle');
    sheet.getRange(2, 1, lastRow - 1, 1).setNumberFormat('dd.MM.yyyy HH:mm:ss');
  }

  sheet.setColumnWidth(1, 150);
  sheet.setColumnWidth(2, 320);
  sheet.setColumnWidth(3, 220);
  sheet.setColumnWidth(4, 100);
  sheet.setColumnWidth(5, 220);
  sheet.setColumnWidth(6, 220);
  sheet.setColumnWidth(7, 220);
  sheet.setColumnWidth(8, 380);
}

/*************** ПАПКИ ***************/
function getWorkFolders_() {
  const rootFolder = DriveApp.getFolderById(ACTS_FOLDER_ID);
  const docsFolder = getOrCreateSubfolder_(rootFolder, DOCS_FOLDER_NAME);
  const pdfFolder = getOrCreateSubfolder_(rootFolder, PDF_FOLDER_NAME);
  return { rootFolder, docsFolder, pdfFolder };
}

function getOrCreateFolder_(folderName) {
  const folders = DriveApp.getFoldersByName(folderName);
  return folders.hasNext() ? folders.next() : DriveApp.createFolder(folderName);
}

function getOrCreateSubfolder_(parentFolder, subfolderName) {
  const folders = parentFolder.getFoldersByName(subfolderName);
  return folders.hasNext() ? folders.next() : parentFolder.createFolder(subfolderName);
}

/*************** СБРОС ***************/
function resetAllProgress() {
  const props = PropertiesService.getScriptProperties();
  [
    'create_last_index',
    'create_count',
    'export_last_index',
    'export_count'
  ].forEach(key => props.deleteProperty(key));

  deleteExistingTriggers_('processCreateDocsBatch');
  deleteExistingTriggers_('processExportDocxBatch');

  SpreadsheetApp.getUi().alert('Прогресс сброшен.');
}

/*************** ОШИБКИ ***************/
function logError_(stage, rowOrIndex, message) {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let logSheet = ss.getSheetByName('Ошибки_актов');

  if (!logSheet) {
    logSheet = ss.insertSheet('Ошибки_актов');
    logSheet.appendRow(['Дата/время', 'Этап', 'Строка/индекс', 'Ошибка']);
  }

  logSheet.appendRow([new Date(), stage, rowOrIndex, message]);
}

/*************** ВСПОМОГАТЕЛЬНЫЕ ***************/
function findFileByName_(folderOrName, name, mimeType) {
  // Поддерживает оба варианта вызова:
  // 1) findFileByName_('file.pdf') — поиск в корневой папке ACTS_FOLDER_ID;
  // 2) findFileByName_(folder, 'file.pdf', MimeType.GOOGLE_DOCS) — поиск в конкретной папке.
  let folder;
  let fileName;

  if (folderOrName && typeof folderOrName.getFilesByName === 'function') {
    folder = folderOrName;
    fileName = name;
  } else {
    folder = DriveApp.getFolderById(ACTS_FOLDER_ID);
    fileName = folderOrName;
  }

  if (!fileName) return null;

  const files = folder.getFilesByName(fileName);
  while (files.hasNext()) {
    const file = files.next();
    if (!mimeType || file.getMimeType() === mimeType) {
      return file;
    }
  }

  return null;
}

function deleteExistingTriggers_(functionName) {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === functionName) {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}

function safeCell_(row, index) {
  return String((row[index] ?? '')).trim();
}

function sanitizeFileName_(name) {
  return String(name || 'Документ')
    .replace(/[\\\/:*?"<>|]/g, '_')
    .replace(/\s+/g, ' ')
    .trim();
}

function formatBytes_(bytes) {
  if (!bytes || bytes <= 0) return '0 Б';

  const units = ['Б', 'КБ', 'МБ', 'ГБ'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size = size / 1024;
    unitIndex++;
  }

  return (size >= 10 || unitIndex === 0 ? size.toFixed(0) : size.toFixed(2)) + ' ' + units[unitIndex];
}

function stripFileExtension_(fileName) {
  const name = String(fileName || '').trim();
  if (!name) return '';

  // Убирает только последнее расширение:
  // file.pdf -> file
  // archive.tar.gz -> archive.tar
  return name.replace(/\.[^.]+$/, '');
}

/*************** СРАВНЕНИЕ С ПЕРВЫМ ЛИСТОМ ***************/
function matchFilesListWithFirstSheet() {
  requireAdmin_();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sourceSheet = SHEET_NAME ? ss.getSheetByName(SHEET_NAME) : ss.getSheets()[0];
  const filesSheet = ss.getSheetByName(FILES_LIST_SHEET_NAME);

  if (!sourceSheet) throw new Error('Первый лист не найден.');
  if (!filesSheet) throw new Error('Лист "Список_файлов" не найден.');

  const sourceLastRow = sourceSheet.getLastRow();
  if (sourceLastRow < 2) {
    SpreadsheetApp.getUi().alert('На первом листе нет данных для сравнения.');
    return;
  }

  const sourceValues = sourceSheet.getRange(2, 1, sourceLastRow - 1, 1).getDisplayValues()
    .flat()
    .map(v => String(v || '').trim())
    .filter(Boolean);

  const filesLastRow = filesSheet.getLastRow();
  if (filesLastRow < 2) {
    SpreadsheetApp.getUi().alert('На листе "Список_файлов" нет данных для сравнения.');
    return;
  }

  const fileNames = filesSheet.getRange(2, 2, filesLastRow - 1, 1).getDisplayValues().flat();

  const results = fileNames.map(fileName => {
    const matched = findBestMatchFromList_(String(fileName || '').trim(), sourceValues);
    return [matched];
  });

  filesSheet.getRange(2, 8, results.length, 1).setValues(results);

  SpreadsheetApp.getUi().alert('Сопоставление завершено.');
}

function findBestMatchFromList_(fileName, sourceList) {
  if (!fileName) return '';

  const fileNorm = normalizeStreetName_(fileName);
  if (!fileNorm) return '';

  // 1. Точное совпадение после нормализации
  for (let i = 0; i < sourceList.length; i++) {
    const src = sourceList[i];
    if (normalizeStreetName_(src) === fileNorm) {
      return src;
    }
  }

  // 2. Частичное вхождение
  for (let i = 0; i < sourceList.length; i++) {
    const src = sourceList[i];
    const srcNorm = normalizeStreetName_(src);

    if (!srcNorm) continue;

    if (srcNorm.indexOf(fileNorm) !== -1 || fileNorm.indexOf(srcNorm) !== -1) {
      return src;
    }
  }

  // 3. Лучшее совпадение по токенам
  let bestValue = '';
  let bestScore = 0;

  const fileTokens = tokenizeStreetName_(fileNorm);

  for (let i = 0; i < sourceList.length; i++) {
    const src = sourceList[i];
    const srcNorm = normalizeStreetName_(src);
    const srcTokens = tokenizeStreetName_(srcNorm);

    const score = calcTokenSimilarity_(fileTokens, srcTokens);

    if (score > bestScore) {
      bestScore = score;
      bestValue = src;
    }
  }

  return bestScore >= 0.55 ? bestValue : '';
}

function normalizeStreetName_(value) {
  let s = String(value || '').toLowerCase().trim();
  if (!s) return '';

  s = s
    .replace(/[«»"']/g, '')
    .replace(/[().,;:]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const replacements = [
    [/\bулица\b/g, 'ул'],
    [/\bул\.\b/g, 'ул'],
    [/\bул\b/g, 'ул'],

    [/\bшоссе\b/g, 'ш'],
    [/\bш\.\b/g, 'ш'],
    [/\bш\b/g, 'ш'],

    [/\bпроезд\b/g, 'пр'],
    [/\bпр\.\b/g, 'пр'],
    [/\bпр\b/g, 'пр'],

    [/\bпереулок\b/g, 'пер'],
    [/\bпер\.\b/g, 'пер'],
    [/\bпер\b/g, 'пер'],

    [/\bтупик\b/g, 'туп'],
    [/\bтуп\.\b/g, 'туп'],
    [/\bтуп\b/g, 'туп'],

    [/\bбульвар\b/g, 'бул'],
    [/\bбул\.\b/g, 'бул'],
    [/\bбул\b/g, 'бул'],

    [/\bплощадь\b/g, 'пл'],
    [/\bпл\.\b/g, 'пл'],
    [/\bпл\b/g, 'пл'],

    [/\bнабережная\b/g, 'наб'],
    [/\bнаб\.\b/g, 'наб'],
    [/\bнаб\b/g, 'наб'],

    [/\bпроспект\b/g, 'просп'],
    [/\bпр-т\b/g, 'просп'],
    [/\bпросп\.\b/g, 'просп'],
    [/\bпросп\b/g, 'просп']
  ];

  replacements.forEach(pair => {
    s = s.replace(pair[0], pair[1]);
  });

  s = s
    .replace(/\s+/g, ' ')
    .trim();

  return s;
}

function tokenizeStreetName_(normalizedValue) {
  return String(normalizedValue || '')
    .split(' ')
    .map(x => x.trim())
    .filter(Boolean);
}

function calcTokenSimilarity_(tokensA, tokensB) {
  if (!tokensA.length || !tokensB.length) return 0;

  const setB = {};
  tokensB.forEach(t => setB[t] = true);

  let common = 0;
  tokensA.forEach(t => {
    if (setB[t]) common++;
  });

  return common / Math.max(tokensA.length, tokensB.length);
}

/*************** ЭКСПОРТ КОЛИЧЕСТВА СТРАНИЦ PDF ПО ПАКЕТАМ ***************/
function startExportPdfPageCounts() {
  deleteExistingTriggers_('processExportPdfPageCountsBatch');

  const props = PropertiesService.getScriptProperties();
  props.deleteProperty('pdf_export_index');
  props.deleteProperty('pdf_export_total');
  props.deleteProperty('pdf_export_done');
  props.deleteProperty('pdf_export_errors');

  const sheet = getOrCreatePdfPagesSheet_();
  clearPdfPagesSheetData_(sheet);

  processExportPdfPageCountsBatch();
}

function processExportPdfPageCountsBatch() {
  deleteExistingTriggers_('processExportPdfPageCountsBatch');

  const props = PropertiesService.getScriptProperties();
  const folder = getOrCreateFolder_(UPLOADS_FOLDER_NAME);
  const sheet = getOrCreatePdfPagesSheet_();
  const cache = loadPdfPagesCache_();

  const allPdfFiles = [];
  const iter = folder.getFiles();

  while (iter.hasNext()) {
    const file = iter.next();
    const fileName = file.getName();
    const lowerName = String(fileName || '').toLowerCase();
    const mimeType = file.getMimeType() || '';
    const isPdf = mimeType === MimeType.PDF || lowerName.endsWith('.pdf');

    if (isPdf) {
      allPdfFiles.push(file);
    }
  }

  let startIndex = Number(props.getProperty('pdf_export_index') || '0');
  let doneCount = Number(props.getProperty('pdf_export_done') || '0');
  let errorCount = Number(props.getProperty('pdf_export_errors') || '0');

  props.setProperty('pdf_export_total', String(allPdfFiles.length));

  const endIndex = Math.min(startIndex + PDF_SCAN_BATCH_SIZE, allPdfFiles.length);
  const rows = [];

  for (let i = startIndex; i < endIndex; i++) {
    const file = allPdfFiles[i];
    const fileName = file.getName();
    const fileId = file.getId();
    const updatedAt = safeDateKey_(file.getLastUpdated());
    const cacheKey = fileId;

    let pageCount = '';
    let status = 'OK';

    try {
      const cached = cache[cacheKey];
      if (cached && cached.updatedAt === updatedAt && cached.pageCount !== '') {
        pageCount = cached.pageCount;
        status = 'OK (кэш)';
      } else {
        const blob = file.getBlob();
        pageCount = getPdfPageCountFast_(blob);
        cache[cacheKey] = {
          updatedAt: updatedAt,
          pageCount: pageCount,
          fileName: fileName
        };
      }
      doneCount++;
    } catch (e) {
      status = 'Ошибка: ' + e.message;
      errorCount++;
      cache[cacheKey] = {
        updatedAt: updatedAt,
        pageCount: '',
        fileName: fileName,
        error: e.message
      };
    }

    rows.push([
      stripFileExtension_(fileName),
      pageCount,
      status,
      fileId
    ]);
  }

  if (rows.length) {
    appendPdfRowsBulk_(sheet, rows);
  }

  savePdfPagesCache_(cache);

  props.setProperty('pdf_export_index', String(endIndex));
  props.setProperty('pdf_export_done', String(doneCount));
  props.setProperty('pdf_export_errors', String(errorCount));

  if (endIndex < allPdfFiles.length) {
    ScriptApp.newTrigger('processExportPdfPageCountsBatch')
      .timeBased()
      .after(10000)
      .create();

    SpreadsheetApp.getActive().toast(
      'PDF: ' + endIndex + ' из ' + allPdfFiles.length,
      'Экспорт страниц PDF',
      10
    );
  } else {
    deleteExistingTriggers_('processExportPdfPageCountsBatch');
    formatPdfPagesSheet_();

    SpreadsheetApp.getUi().alert(
      'Экспорт страниц PDF завершён.\n' +
      'PDF найдено: ' + allPdfFiles.length + '\n' +
      'Успешно: ' + doneCount + '\n' +
      'С ошибками: ' + errorCount
    );
  }
}

function resetPdfPageCountsProgress() {
  deleteExistingTriggers_('processExportPdfPageCountsBatch');

  const props = PropertiesService.getScriptProperties();
  props.deleteProperty('pdf_export_index');
  props.deleteProperty('pdf_export_total');
  props.deleteProperty('pdf_export_done');
  props.deleteProperty('pdf_export_errors');

  SpreadsheetApp.getUi().alert('Прогресс экспорта страниц PDF сброшен.');
}

function getOrCreatePdfPagesSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(PDF_PAGES_SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(PDF_PAGES_SHEET_NAME);
  }

  sheet.getRange(1, 1, 1, 4).setValues([[
    'Наименование файла',
    'Количество страниц',
    'Статус',
    'ID файла в Drive'
  ]]);

  sheet.setFrozenRows(1);
  return sheet;
}

function clearPdfPagesSheetData_(sheet) {
  const lastRow = sheet.getLastRow();
  const lastCol = Math.max(sheet.getLastColumn(), 4);

  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, lastCol).clearContent();
  }
}

function appendPdfRowsBulk_(sheet, rows) {
  if (!rows || !rows.length) return;

  const startRow = sheet.getLastRow() + 1;
  sheet.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
}

function formatPdfPagesSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(PDF_PAGES_SHEET_NAME);
  if (!sheet) return;

  const lastRow = Math.max(sheet.getLastRow(), 1);

  sheet.getRange(1, 1, 1, 4)
    .setFontWeight('bold')
    .setBackground('#d9ead3');

  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, 4).setVerticalAlignment('middle');
  }

  sheet.setColumnWidth(1, 320);
  sheet.setColumnWidth(2, 150);
  sheet.setColumnWidth(3, 260);
  sheet.setColumnWidth(4, 220);
}

function getPdfPageCountFast_(blob) {
  const text = blob.getDataAsString('ISO-8859-1');

  if (!text || text.indexOf('%PDF') === -1) {
    throw new Error('Файл не распознан как PDF');
  }

  let maxCount = 0;
  let match;
  const countRegex = /\/Count\s+(\d+)/g;

  while ((match = countRegex.exec(text)) !== null) {
    const n = Number(match[1]);
    if (!isNaN(n) && n > maxCount) {
      maxCount = n;
    }
  }

  if (maxCount > 0) {
    return maxCount;
  }

  const pageMatches = text.match(/\/Type\s*\/Page\b/g);
  const pageCountByType = pageMatches ? pageMatches.length : 0;

  if (pageCountByType > 0) {
    return pageCountByType;
  }

  throw new Error('Не удалось определить количество страниц');
}

function loadPdfPagesCache_() {
  try {
    const raw = PropertiesService.getScriptProperties().getProperty(PDF_CACHE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function savePdfPagesCache_(cache) {
  PropertiesService.getScriptProperties().setProperty(
    PDF_CACHE_KEY,
    JSON.stringify(cache || {})
  );
}

function safeDateKey_(dateObj) {
  if (!dateObj) return '';
  return Utilities.formatDate(
    new Date(dateObj),
    Session.getScriptTimeZone(),
    'yyyy-MM-dd HH:mm:ss'
  );
}

/*************** ПЕРЕИМЕНОВАНИЕ PDF ПО ЛИСТУ "Список_файлов" ***************/
function renamePdfFilesByFilesList() {
  requireAdmin_();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(FILES_LIST_SHEET_NAME);

  if (!sheet) throw new Error('Лист не найден');

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;

  const folders = getWorkFolders_();
  const pdfFolder = folders.pdfFolder;

  const data = sheet.getRange(2, 2, lastRow - 1, 7).getDisplayValues();

  // 🚀 1. Загружаем ВСЕ PDF в карту (очень быстро)
  const fileMap = {};
  const iter = pdfFolder.getFiles();

  while (iter.hasNext()) {
    const file = iter.next();
    const name = file.getName();

    const clean = normalizeFast_(name);
    const cleanNoPrefix = normalizeFast_(stripLeadingNumberPrefix_(stripFileExtension_(name)));

    fileMap[clean] = file;
    fileMap[cleanNoPrefix] = file;
  }

  // 🚀 2. Обработка
  const updates = [];
  let renamed = 0;
  let skipped = 0;
  let notFound = 0;

  data.forEach((row, i) => {
    const sheetRow = i + 2;

    const newName = safeStringForRename_(row[0]); // B
    const current = safeStringForRename_(row[6]); // H

    if (!newName || !current) {
      skipped++;
      return;
    }

    const key = normalizeFast_(current);
    const file = fileMap[key];

    if (!file) {
      notFound++;
      return;
    }

    const targetName = ensurePdfExtension_(sanitizeDriveFileName_(newName));

    if (file.getName() === targetName) {
      skipped++;
      return;
    }

    try {
      file.setName(targetName);
      renamed++;
    } catch (e) {
      Logger.log('Ошибка: ' + e.message);
    }
  });

  SpreadsheetApp.getUi().alert(
    'Готово\n' +
    'Переименовано: ' + renamed + '\n' +
    'Пропущено: ' + skipped + '\n' +
    'Не найдено: ' + notFound
  );
}

function findMatchingPdfFile_(pdfFiles, objectNameFromH) {
  const targetNorm = normalizePdfLookupName_(objectNameFromH);

  if (!targetNorm) return null;

  // 1. Точное совпадение по нормализованному имени
  for (let i = 0; i < pdfFiles.length; i++) {
    const file = pdfFiles[i];
    const fileNorm = normalizePdfLookupName_(file.getName());
    if (fileNorm === targetNorm) {
      return file;
    }
  }

  // 2. Совпадение, если у PDF есть префикс "123 - "
  for (let i = 0; i < pdfFiles.length; i++) {
    const file = pdfFiles[i];
    const raw = stripFileExtension_(file.getName());
    const withoutPrefix = stripLeadingNumberPrefix_(raw);
    const fileNorm = normalizePdfLookupName_(withoutPrefix);

    if (fileNorm === targetNorm) {
      return file;
    }
  }

  // 3. Частичное совпадение
  for (let i = 0; i < pdfFiles.length; i++) {
    const file = pdfFiles[i];
    const raw = stripFileExtension_(file.getName());
    const withoutPrefix = stripLeadingNumberPrefix_(raw);
    const fileNorm = normalizePdfLookupName_(withoutPrefix);

    if (!fileNorm) continue;

    if (fileNorm.indexOf(targetNorm) !== -1 || targetNorm.indexOf(fileNorm) !== -1) {
      return file;
    }
  }

  return null;
}

function normalizePdfLookupName_(value) {
  let s = stripFileExtension_(String(value || '').trim().toLowerCase());
  if (!s) return '';

  s = stripLeadingNumberPrefix_(s);

  s = s
    .replace(/[«»"']/g, '')
    .replace(/[().,;:]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  return s;
}

function stripLeadingNumberPrefix_(value) {
  return String(value || '')
    .replace(/^\d+\s*-\s*/g, '')
    .trim();
}

function ensurePdfExtension_(name) {
  const s = String(name || '').trim();
  if (!s) return '';
  return /\.pdf$/i.test(s) ? s : s + '.pdf';
}

function sanitizeDriveFileName_(name) {
  return String(name || '')
    .replace(/[\\\/:*?"<>|]/g, '_')
    .replace(/\s+/g, ' ')
    .trim();
}

function safeStringForRename_(value) {
  return String(value == null ? '' : value).trim();
}

function writePdfRenameLog_(rows) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheetName = 'Лог_переименования_PDF';
  let sheet = ss.getSheetByName(sheetName);

  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    sheet.getRange(1, 1, 1, 5).setValues([[
      'Дата/время',
      'Строка листа "Список_файлов"',
      'Исходное значение / старое имя',
      'Новое имя',
      'Статус'
    ]]);
    sheet.setFrozenRows(1);
  }

  if (rows && rows.length) {
    const startRow = sheet.getLastRow() + 1;
    sheet.getRange(startRow, 1, rows.length, 5).setValues(rows);
  }

  sheet.getRange(1, 1, 1, 5)
    .setFontWeight('bold')
    .setBackground('#d9ead3');

  sheet.setColumnWidth(1, 150);
  sheet.setColumnWidth(2, 120);
  sheet.setColumnWidth(3, 320);
  sheet.setColumnWidth(4, 320);
  sheet.setColumnWidth(5, 220);
}

function normalizeFast_(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[«»"']/g, '')
    .replace(/[().,;:]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function debugSingleActObjects() {
  const items = getObjectsForSingleAct();
  Logger.log('Количество объектов: ' + items.length);
  if (items.length) {
    Logger.log(JSON.stringify(items.slice(0, 10)));
  }
}


/*************** СВЯЗКА PDF С GOOGLE DRIVE ***************/
function getDrivePdfMergeModuleData() {
  requireActiveUser_();
  return {
    mainFiles: listPdfFilesFromFolder_(PDF_MAIN_3P_FOLDER_ID),
    appendFiles: listPdfFilesFromFolder_(PDF_APPEND_4P_FOLDER_ID)
  };
}

function listPdfFilesFromFolder_(folderId) {
  const folder = DriveApp.getFolderById(folderId);
  const files = folder.getFiles();
  const result = [];
  while (files.hasNext()) {
    const file = files.next();
    const name = file.getName();
    const mimeType = file.getMimeType();
    if (mimeType === MimeType.PDF || /\.pdf$/i.test(name)) {
      result.push({
        id: file.getId(),
        name: name,
        url: file.getUrl(),
        size: file.getSize(),
        updated: Utilities.formatDate(file.getLastUpdated(), Session.getScriptTimeZone(), 'dd.MM.yyyy HH:mm')
      });
    }
  }
  result.sort((a, b) => String(a.name).localeCompare(String(b.name), 'ru'));
  return result;
}

function getDrivePdfAsBase64(fileId) {
  requireActiveUser_();
  if (!fileId) throw new Error('Не передан ID PDF-файла.');
  const file = DriveApp.getFileById(String(fileId));
  const name = file.getName();
  if (file.getMimeType() !== MimeType.PDF && !/\.pdf$/i.test(name)) {
    throw new Error('Файл "' + name + '" не является PDF.');
  }
  return {
    id: file.getId(),
    name: name,
    base64: Utilities.base64Encode(file.getBlob().getBytes()),
    url: file.getUrl(),
    size: file.getSize()
  };
}

function saveMergedDrivePdf(payload) {
  requireAdmin_();
  const data = payload || {};
  if (!data.fileName || !data.base64) throw new Error('Не переданы данные объединенного PDF.');
  const rootFolder = DriveApp.getFolderById(ACTS_FOLDER_ID);
  const targetFolder = getOrCreateSubfolder_(rootFolder, 'Связанные PDF');
  const fileName = ensurePdfExtension_(sanitizePdfFileName_(data.fileName));
  const bytes = Utilities.base64Decode(String(data.base64));
  const blob = Utilities.newBlob(bytes, MimeType.PDF, fileName);
  const file = targetFolder.createFile(blob);
  logPlatformChange_('acts', 'saveMergedPdf', file.getId(), {
    fileName: file.getName(),
    fileId: file.getId(),
    url: file.getUrl()
  });
  return {
    fileName: file.getName(),
    fileId: file.getId(),
    url: file.getUrl(),
    folderUrl: targetFolder.getUrl()
  };
}

/*************** ОБРАБОТКА ЗАГРУЖЕННЫХ PDF И СОХРАНЕНИЕ НА ДИСК ***************/
function saveManagedPdfFiles(payload) {
  requireAdmin_();
  const data = payload || {};
  const files = Array.isArray(data.files) ? data.files : [];
  if (!files.length) {
    throw new Error('Не переданы PDF-файлы для сохранения.');
  }

  const rootFolder = DriveApp.getFolderById(ACTS_FOLDER_ID);
  const targetFolder = getOrCreateSubfolder_(rootFolder, 'Обработанные PDF');
  const saved = [];
  const errors = [];

  files.forEach(item => {
    const sourceName = String(item.fileName || '').trim();
    try {
      if (!sourceName) throw new Error('Не указано имя файла.');
      if (!item.base64) throw new Error('Не передано содержимое файла.');

      const fileName = ensurePdfExtension_(sanitizePdfFileName_(sourceName));
      const bytes = Utilities.base64Decode(String(item.base64));
      const blob = Utilities.newBlob(bytes, MimeType.PDF, fileName);
      const file = targetFolder.createFile(blob);

      saved.push({
        fileName: file.getName(),
        fileId: file.getId(),
        url: file.getUrl(),
        pageCount: item.pageCount || '',
        status: item.status || ''
      });
    } catch (e) {
      errors.push({
        fileName: sourceName || 'PDF без имени',
        message: e && e.message ? e.message : String(e)
      });
    }
  });

  logPlatformChange_('acts', 'saveManagedPdfFiles', 'processed', {
    saved: saved.length,
    errors: errors.length
  });
  return {
    success: errors.length === 0,
    saved: saved,
    errors: errors,
    folderUrl: targetFolder.getUrl()
  };
}

function sanitizePdfFileName_(name) {
  return String(name || 'document.pdf')
    .replace(/[\\/:*?"<>|]/g, '_')
    .replace(/\s+/g, ' ')
    .trim() || 'document.pdf';
}


/*************** ВЕБ-САЙТ: СТАТУСЫ РАБОТ ***************/
const SHEET_WORK_STATUSES_KBU = 'Статусы_КБУ';
const SHEET_WORK_STATUSES_TEKREM = 'Статусы_ТекРем';
const SHEET_WORK_STATUSES_KBU_UPDATE = 'Статусы_КБУ_обновление';
const SHEET_WORK_STATUSES_TEKREM_UPDATE = 'Статусы_ТекРем_обновление';
const SHEET_WORK_EXECUTORS = 'Статусы_Исполнитель';
const WORK_STATUS_ACTUALIZATION_HEADER = 'Актуализация данных';

function getWorkStatusesData() {
  requireActiveUser_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const executorSheet = ss.getSheetByName(SHEET_WORK_EXECUTORS);
  const executorInfo = readWorkStatusExecutors_(executorSheet);
  const kbuSheet = ss.getSheetByName(SHEET_WORK_STATUSES_KBU);
  const tekremSheet = ss.getSheetByName(SHEET_WORK_STATUSES_TEKREM);
  const kbuUpdateSheet = ss.getSheetByName(SHEET_WORK_STATUSES_KBU_UPDATE);
  const tekremUpdateSheet = ss.getSheetByName(SHEET_WORK_STATUSES_TEKREM_UPDATE);
  const kbuUpdateMap = buildWorkStatusUpdateMap_(kbuUpdateSheet, 'kbu');
  const tekremUpdateMap = buildWorkStatusUpdateMap_(tekremUpdateSheet, 'tekrem');
  const financeMap = buildWorkStatusFinanceMap_(ss, 2026);
  const kbu = readWorkStatusKbu_(kbuSheet, executorInfo.map, kbuUpdateMap, financeMap.kbu);
  const tekrem = readWorkStatusTekRem_(tekremSheet, executorInfo.map, tekremUpdateMap, financeMap.tekrem);
  const items = kbu.concat(tekrem);
  const needActualization = items.filter(x => x.needActualization).length;
  return {
    items: items,
    planStart: executorInfo.planStart,
    planEnd: executorInfo.planEnd,
    executors: Object.keys(executorInfo.map).sort(),
    total: items.length,
    needActualization: needActualization
  };
}


function buildWorkStatusFinanceMap_(ss, year) {
  const result = { kbu: {}, tekrem: {} };
  const y = normalizeTitleYear_(year || 2026);

  const kbuSheet = ss.getSheetByName('Титул_КБУ' + y + '_СМР');
  if (kbuSheet && kbuSheet.getLastRow() >= 2) {
    const lastRow = kbuSheet.getLastRow();
    const values = kbuSheet.getRange(2, 1, lastRow - 1, Math.max(18, kbuSheet.getLastColumn())).getDisplayValues();
    values.forEach(r => {
      const street = String(r[1] || '').replace(/\s+/g, ' ').trim(); // B — Наименование улицы
      const cost = parseWorkFinanceNumber_(r[17]); // R — Стоимость работ
      if (!street || !cost) return;
      const key = normalizeWorkCompare_(street);
      result.kbu[key] = (result.kbu[key] || 0) + cost;
    });
  }

  const tekremSheet = ss.getSheetByName('Титул_ТекРем' + y);
  if (tekremSheet && tekremSheet.getLastRow() >= 2) {
    const lastRow = tekremSheet.getLastRow();
    const values = tekremSheet.getRange(2, 1, lastRow - 1, Math.max(11, tekremSheet.getLastColumn())).getDisplayValues();
    values.forEach(r => {
      const objectName = String(r[0] || '').replace(/\s+/g, ' ').trim(); // A — Наименование объекта
      const cost = parseWorkFinanceNumber_(r[10]); // K — Стоимость работ
      if (!objectName || !cost) return;
      const key = normalizeWorkCompare_(objectName);
      result.tekrem[key] = (result.tekrem[key] || 0) + cost;
    });
  }

  return result;
}

function parseWorkFinanceNumber_(value) {
  if (typeof value === 'number') return isFinite(value) ? value : 0;
  const s = String(value || '')
    .replace(/\u00A0/g, ' ')
    .replace(/[^0-9,\.\- ]/g, '')
    .replace(/\s+/g, '')
    .replace(',', '.');
  const n = Number(s);
  return isFinite(n) ? n : 0;
}

function applyWorkFinanceToItem_(item, fullCost) {
  const cost = Number(fullCost) || 0;
  item.financingFull = cost;
  item.financing80 = cost ? cost * 0.8 : 0;
  item.financing80Display = cost ? formatFinanceWeb_(cost * 0.8) : '';
  item.financingFullDisplay = cost ? formatFinanceWeb_(cost) : '';
  return item;
}

function formatFinanceWeb_(value) {
  const n = Number(value) || 0;
  return n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function readWorkStatusExecutors_(sheet) {
  const result = { map: {}, planStart: '', planEnd: '' };
  if (!sheet) return result;
  result.planStart = formatDateWeb_(sheet.getRange('F2').getValue() || sheet.getRange('F2').getDisplayValue());
  result.planEnd = formatDateWeb_(sheet.getRange('G2').getValue() || sheet.getRange('G2').getDisplayValue());
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return result;
  const values = sheet.getRange(2, 1, lastRow - 1, Math.max(3, sheet.getLastColumn())).getDisplayValues();
  values.forEach(r => {
    const executor = String(r[0] || '').replace(/\s+/g, ' ').trim();
    if (!executor) return;
    result.map[normalizeWeb_(executor)] = {
      executor: executor,
      contractDate: String(r[1] || '').trim(),
      inn: String(r[2] || '').trim()
    };
  });
  return result;
}

function readWorkStatusKbu_(sheet, executorMap, updateMap, financeMap) {
  if (!sheet || sheet.getLastRow() < 2) return [];
  const actualCol = ensureWorkStatusActualizationColumn_(sheet, 11);
  const lastRow = sheet.getLastRow();
  const values = sheet.getRange(2, 1, lastRow - 1, Math.max(actualCol, 11)).getDisplayValues();
  const rawItems = values.map((r, idx) => {
    const executor = String(r[4] || '').trim();
    const info = findWorkExecutorInfo_(executorMap, executor);
    const item = {
      source: 'kbu',
      sourceLabel: 'КБУ',
      rowNumber: idx + 2,
      rowNumbers: [idx + 2],
      idOdx: String(r[0] || '').trim(),
      streetName: String(r[1] || '').trim(),
      objectName: String(r[2] || '').trim(),
      district: String(r[3] || '').trim(),
      executor: executor,
      startDate: String(r[5] || '').trim(),
      endDate: String(r[6] || '').trim(),
      status: String(r[7] || '').trim(),
      peopleCount: String(r[8] || '').trim(),
      vehiclesCount: String(r[9] || '').trim(),
      contractDate: info.contractDate || '',
      inn: info.inn || '',
      actualization: isWorkActualized_(r[actualCol - 1])
    };
    enrichWorkStatusItemWithUpdate_(item, updateMap);
    return item;
  }).filter(x => x.objectName || x.streetName || x.idOdx);
  return groupWorkStatusKbuByStreet_(rawItems, financeMap || {});
}

function groupWorkStatusKbuByStreet_(items, financeMap) {
  const groups = {};
  (items || []).forEach(item => {
    const key = normalizeWorkCompare_(item.streetName || item.objectName || item.idOdx);
    if (!key) return;
    if (!groups[key]) {
      groups[key] = {
        source: 'kbu',
        sourceLabel: 'КБУ',
        isGroupedStreet: true,
        groupKey: key,
        rowNumbers: [],
        rowNumber: '',
        updateRowNumbers: [],
        idOdxList: [],
        idOdx: '',
        streetName: item.streetName || item.objectName || '',
        objectName: item.streetName || item.objectName || '',
        objects: [],
        district: '',
        executor: '',
        startDate: '',
        endDate: '',
        status: '',
        peopleCount: '',
        vehiclesCount: '',
        contractDate: '',
        inn: '',
        financingFull: 0,
        financing80: 0,
        financingFullDisplay: '',
        financing80Display: '',
        actualization: true,
        needActualization: false,
        importantActualization: false,
        statusChangedToImportant: false,
        changes: [],
        resourceChanges: [],
        targetStatus: '',
        actualizationTarget: null
      };
    }
    const g = groups[key];
    g.rowNumbers.push(item.rowNumber);
    if (item.updateRowNumber) g.updateRowNumbers.push(item.updateRowNumber);
    if (item.idOdx) g.idOdxList.push(item.idOdx);
    if (item.objectName && g.objects.indexOf(item.objectName) === -1) g.objects.push(item.objectName);
    g.actualization = g.actualization && !!item.actualization;
    g.needActualization = g.needActualization || !!item.needActualization;
    g.importantActualization = g.importantActualization || !!item.importantActualization;
    g.statusChangedToImportant = g.statusChangedToImportant || !!item.statusChangedToImportant;
    (item.changes || []).forEach(ch => {
      const prefix = item.objectName || item.idOdx || 'объект';
      g.changes.push({
        field: ch.field,
        label: prefix + ' — ' + ch.label,
        oldValue: ch.oldValue,
        newValue: ch.newValue
      });
    });
    (item.resourceChanges || []).forEach(ch => {
      const prefix = item.objectName || item.idOdx || 'объект';
      g.resourceChanges.push({
        field: ch.field,
        label: prefix + ' — ' + ch.label,
        oldValue: ch.oldValue,
        newValue: ch.newValue
      });
    });
    if (item.targetStatus && !g.targetStatus) g.targetStatus = item.targetStatus;
  });

  return Object.keys(groups).map(key => {
    const g = groups[key];
    const sourceItems = (items || []).filter(x => normalizeWorkCompare_(x.streetName || x.objectName || x.idOdx) === key);
    g.rowNumbers = uniqueWorkArray_(g.rowNumbers).sort((a,b) => Number(a) - Number(b));
    g.updateRowNumbers = uniqueWorkArray_(g.updateRowNumbers).sort((a,b) => Number(a) - Number(b));
    g.idOdxList = uniqueWorkArray_(g.idOdxList);
    g.rowNumber = g.rowNumbers.join(',');
    g.idOdx = g.idOdxList.length === 1 ? g.idOdxList[0] : 'Объектов: ' + g.rowNumbers.length;
    g.district = joinUniformWorkValues_(sourceItems.map(x => x.district));
    g.executor = joinUniformWorkValues_(sourceItems.map(x => x.executor));
    g.startDate = joinUniformWorkValues_(sourceItems.map(x => x.startDate));
    g.endDate = joinUniformWorkValues_(sourceItems.map(x => x.endDate));
    g.status = joinUniformWorkValues_(sourceItems.map(x => x.status));
    g.targetStatus = joinUniformWorkValues_(sourceItems.map(x => x.targetStatus)) || g.status;
    g.peopleCount = sumOrUniformWorkValues_(sourceItems.map(x => x.peopleCount));
    g.vehiclesCount = sumOrUniformWorkValues_(sourceItems.map(x => x.vehiclesCount));
    g.contractDate = joinUniformWorkValues_(sourceItems.map(x => x.contractDate));
    g.inn = joinUniformWorkValues_(sourceItems.map(x => x.inn));
    applyWorkFinanceToItem_(g, (financeMap || {})[key] || 0);
    g.actualizationTarget = null;
    return g;
  }).sort((a, b) => String(a.streetName || '').localeCompare(String(b.streetName || ''), 'ru'));
}

function uniqueWorkArray_(arr) {
  return Array.from(new Set((arr || []).filter(v => v !== '' && v !== null && v !== undefined)));
}

function joinUniformWorkValues_(values) {
  const clean = uniqueWorkArray_((values || []).map(v => String(v || '').trim()).filter(Boolean));
  if (!clean.length) return '';
  return clean.length === 1 ? clean[0] : 'Разные значения';
}

function sumOrUniformWorkValues_(values) {
  const clean = (values || []).map(v => String(v || '').trim()).filter(Boolean);
  if (!clean.length) return '';
  let canSum = true;
  const nums = clean.map(v => {
    const n = Number(String(v).replace(/\s+/g, '').replace(',', '.'));
    if (!isFinite(n)) canSum = false;
    return n;
  });
  if (canSum) return String(nums.reduce((a,b) => a + b, 0));
  return joinUniformWorkValues_(clean);
}

function readWorkStatusTekRem_(sheet, executorMap, updateMap, financeMap) {
  if (!sheet || sheet.getLastRow() < 2) return [];
  const actualCol = ensureWorkStatusActualizationColumn_(sheet, 11);
  const lastRow = sheet.getLastRow();
  const values = sheet.getRange(2, 1, lastRow - 1, Math.max(actualCol, 10)).getDisplayValues();
  const excluded = {'дкр (ргс)': true, 'дкр (ртс)': true};
  const rawItems = values.map((r, idx) => {
    const program = String(r[0] || '').replace(/\s+/g, ' ').trim();
    if (excluded[program.toLowerCase()]) return null;
    const executor = String(r[1] || '').trim();
    const info = findWorkExecutorInfo_(executorMap, executor);
    const item = {
      source: 'tekrem',
      sourceLabel: 'ТекРем',
      rowNumber: idx + 2,
      rowNumbers: [idx + 2],
      program: program,
      executor: executor,
      idOdx: String(r[2] || '').trim(),
      streetName: String(r[3] || '').trim(),
      objectName: String(r[4] || '').trim(),
      status: String(r[5] || '').trim(),
      startDate: String(r[6] || '').trim(),
      endDate: String(r[7] || '').trim(),
      district: '',
      peopleCount: String(r[8] || '').trim(),
      vehiclesCount: String(r[9] || '').trim(),
      contractDate: info.contractDate || '',
      inn: info.inn || '',
      actualization: isWorkActualized_(r[actualCol - 1])
    };
    enrichWorkStatusItemWithUpdate_(item, updateMap);
    return item;
  }).filter(Boolean).filter(x => x.objectName || x.streetName || x.idOdx);
  return groupWorkStatusTekRemByIdOdx_(rawItems, financeMap || {});
}

function groupWorkStatusTekRemByIdOdx_(items, financeMap) {
  const groups = {};
  (items || []).forEach(item => {
    const key = normalizeWorkCompare_(item.idOdx) || normalizeWorkCompare_(item.objectName || item.streetName);
    if (!key) return;
    if (!groups[key]) {
      groups[key] = {
        source: 'tekrem',
        sourceLabel: 'ТекРем',
        isGroupedIdOdx: true,
        groupKey: key,
        rowNumbers: [],
        rowNumber: '',
        updateRowNumbers: [],
        idOdx: item.idOdx || '',
        objectName: item.objectName || item.streetName || '',
        streetName: item.streetName || '',
        objects: [],
        program: '',
        district: '',
        executor: '',
        startDate: '',
        endDate: '',
        status: '',
        peopleCount: '',
        vehiclesCount: '',
        contractDate: '',
        inn: '',
        financingFull: 0,
        financing80: 0,
        financingFullDisplay: '',
        financing80Display: '',
        actualization: true,
        needActualization: false,
        importantActualization: false,
        statusChangedToImportant: false,
        changes: [],
        resourceChanges: [],
        targetStatus: '',
        actualizationTarget: null
      };
    }
    const g = groups[key];
    g.rowNumbers.push(item.rowNumber);
    if (item.updateRowNumber) g.updateRowNumbers.push(item.updateRowNumber);
    if (item.objectName && g.objects.indexOf(item.objectName) === -1) g.objects.push(item.objectName);
    g.actualization = g.actualization && !!item.actualization;
    g.needActualization = g.needActualization || !!item.needActualization;
    g.importantActualization = g.importantActualization || !!item.importantActualization;
    g.statusChangedToImportant = g.statusChangedToImportant || !!item.statusChangedToImportant;
    (item.changes || []).forEach(ch => {
      const prefix = item.objectName || item.streetName || item.idOdx || 'объект';
      g.changes.push({
        field: ch.field,
        label: prefix + ' — ' + ch.label,
        oldValue: ch.oldValue,
        newValue: ch.newValue
      });
    });
    (item.resourceChanges || []).forEach(ch => {
      const prefix = item.objectName || item.streetName || item.idOdx || 'объект';
      g.resourceChanges.push({
        field: ch.field,
        label: prefix + ' — ' + ch.label,
        oldValue: ch.oldValue,
        newValue: ch.newValue
      });
    });
  });

  return Object.keys(groups).map(key => {
    const g = groups[key];
    const sourceItems = (items || []).filter(x => (normalizeWorkCompare_(x.idOdx) || normalizeWorkCompare_(x.objectName || x.streetName)) === key);
    g.rowNumbers = uniqueWorkArray_(g.rowNumbers).sort((a,b) => Number(a) - Number(b));
    g.updateRowNumbers = uniqueWorkArray_(g.updateRowNumbers).sort((a,b) => Number(a) - Number(b));
    g.rowNumber = g.rowNumbers.join(',');
    g.idOdx = joinUniformWorkValues_(sourceItems.map(x => x.idOdx)) || g.idOdx;
    g.objectName = joinUniformWorkValues_(sourceItems.map(x => x.objectName)) || g.objectName;
    g.streetName = joinUniformWorkValues_(sourceItems.map(x => x.streetName)) || g.streetName;
    g.program = joinUniformWorkValues_(sourceItems.map(x => x.program));
    g.executor = joinUniformWorkValues_(sourceItems.map(x => x.executor));
    g.startDate = joinUniformWorkValues_(sourceItems.map(x => x.startDate));
    g.endDate = joinUniformWorkValues_(sourceItems.map(x => x.endDate));
    g.status = joinUniformWorkValues_(sourceItems.map(x => x.status));
    g.targetStatus = joinUniformWorkValues_(sourceItems.map(x => x.targetStatus)) || g.status;
    g.peopleCount = sumOrUniformWorkValues_(sourceItems.map(x => x.peopleCount));
    g.vehiclesCount = sumOrUniformWorkValues_(sourceItems.map(x => x.vehiclesCount));
    g.contractDate = joinUniformWorkValues_(sourceItems.map(x => x.contractDate));
    g.inn = joinUniformWorkValues_(sourceItems.map(x => x.inn));

    const financeKeys = uniqueWorkArray_(sourceItems.map(x => normalizeWorkCompare_(x.objectName || x.streetName)));
    const fullCost = financeKeys.reduce((sum, fk) => sum + (Number((financeMap || {})[fk]) || 0), 0);
    applyWorkFinanceToItem_(g, fullCost);
    g.actualizationTarget = null;
    return g;
  }).sort((a, b) => String(a.objectName || a.streetName || '').localeCompare(String(b.objectName || b.streetName || ''), 'ru'));
}

function buildWorkStatusUpdateMap_(sheet, source) {
  const map = {};
  if (!sheet || sheet.getLastRow() < 2) return map;
  const src = String(source || '').toLowerCase();
  const lastRow = sheet.getLastRow();
  const lastCol = Math.max(sheet.getLastColumn(), src === 'kbu' ? 10 : 10);
  const displayValues = sheet.getRange(2, 1, lastRow - 1, lastCol).getDisplayValues();
  const excluded = {'дкр (ргс)': true, 'дкр (ртс)': true};
  displayValues.forEach((r, idx) => {
    let item;
    if (src === 'kbu') {
      item = {
        source: 'kbu',
        updateRowNumber: idx + 2,
        idOdx: String(r[0] || '').trim(),
        streetName: String(r[1] || '').trim(),
        objectName: String(r[2] || '').trim(),
        district: String(r[3] || '').trim(),
        executor: String(r[4] || '').trim(),
        startDate: String(r[5] || '').trim(),
        endDate: String(r[6] || '').trim(),
        status: String(r[7] || '').trim(),
        peopleCount: String(r[8] || '').trim(),
        vehiclesCount: String(r[9] || '').trim()
      };
    } else if (src === 'tekrem') {
      const program = String(r[0] || '').replace(/\s+/g, ' ').trim();
      if (excluded[program.toLowerCase()]) return;
      item = {
        source: 'tekrem',
        updateRowNumber: idx + 2,
        program: program,
        executor: String(r[1] || '').trim(),
        idOdx: String(r[2] || '').trim(),
        streetName: String(r[3] || '').trim(),
        objectName: String(r[4] || '').trim(),
        status: String(r[5] || '').trim(),
        startDate: String(r[6] || '').trim(),
        endDate: String(r[7] || '').trim(),
        peopleCount: String(r[8] || '').trim(),
        vehiclesCount: String(r[9] || '').trim()
      };
    } else {
      return;
    }
    const key = makeWorkStatusKey_(item);
    if (key) map[key] = item;
  });
  return map;
}

function enrichWorkStatusItemWithUpdate_(item, updateMap) {
  const update = updateMap && updateMap[makeWorkStatusKey_(item)];
  item.updateFound = !!update;
  item.updateRowNumber = update ? update.updateRowNumber : '';
  item.changes = [];
  item.resourceChanges = [];
  item.needActualization = false;
  item.importantActualization = false;
  item.statusChangedToImportant = false;
  item.actualizationTarget = update ? {
    executor: update.executor || '',
    startDate: update.startDate || '',
    endDate: update.endDate || '',
    status: update.status || '',
    peopleCount: update.peopleCount || '',
    vehiclesCount: update.vehiclesCount || ''
  } : null;
  item.targetStatus = update ? (update.status || item.status || '') : (item.status || '');
  if (!update) return item;

  const targetStatus = update.status || item.status || '';
  const targetIsImportant = isImportantWorkStatusValue_(targetStatus);
  const oldStatusValue = normalizeWorkCompare_(item.status);
  const newStatusValue = normalizeWorkCompare_(update.status || item.status || '');
  item.statusChangedToImportant = targetIsImportant && oldStatusValue !== newStatusValue;

  if (!targetIsImportant) {
    // Остальные статусы не требуют актуализации, поэтому изменения по ним не показываем.
    return item;
  }

  const addChange = (key, label) => {
    const oldValue = normalizeWorkCompare_(item[key]);
    const newValue = normalizeWorkCompare_(update[key]);
    if (oldValue !== newValue) {
      item.changes.push({
        field: key,
        label: label,
        oldValue: item[key] || '—',
        newValue: update[key] || '—'
      });
    }
  };

  addChange('status', 'Статус объекта');
  addChange('startDate', 'Дата начала СМР');
  if (isCompletedWorkStatusValue_(targetStatus)) {
    addChange('endDate', 'Дата окончания СМР');
  }

  if (!isCompletedWorkStatusValue_(targetStatus)) {
    [
      ['peopleCount', 'Количество людей'],
      ['vehiclesCount', 'Количество техники']
    ].forEach(([key, label]) => {
      const oldValue = normalizeWorkCompare_(item[key]);
      const newValue = normalizeWorkCompare_(update[key]);
      if (oldValue !== newValue) {
        item.resourceChanges.push({
          field: key,
          label: label,
          oldValue: item[key] || '—',
          newValue: update[key] || '—'
        });
      }
    });
  }

  item.needActualization = item.changes.length > 0 || item.resourceChanges.length > 0;
  // Фильтр особого внимания должен учитывать карточки,
  // где статус изменился на «Подготовительные работы», «В работе» или «Завершен»,
  // а также карточки со статусом «Подготовительные работы» / «В работе»,
  // где поменялись люди или техника. Для «Завершен» изменения ресурсов не выводим.
  item.importantActualization = !!item.statusChangedToImportant || (!isCompletedWorkStatusValue_(targetStatus) && item.resourceChanges.length > 0);
  if (item.needActualization) item.actualization = false;
  return item;
}

function isInProgressWorkStatusValue_(value) {
  return normalizeWorkCompare_(value) === 'в работе';
}

function isResourceWorkStatusValue_(value) {
  const s = normalizeWorkCompare_(value);
  return s === 'подготовительные работы' || s === 'в работе';
}

function isCompletedWorkStatusValue_(value) {
  return normalizeWorkCompare_(value) === 'завершен';
}

function isImportantWorkStatusValue_(value) {
  const s = normalizeWorkCompare_(value);
  return s === 'подготовительные работы' || s === 'в работе' || s === 'завершен';
}

function makeWorkStatusKey_(item) {
  const id = normalizeWorkCompare_(item && item.idOdx);
  if (id) return 'id:' + id;
  const objectName = normalizeWorkCompare_(item && item.objectName);
  const streetName = normalizeWorkCompare_(item && item.streetName);
  if (objectName || streetName) return 'name:' + objectName + '|street:' + streetName;
  return '';
}

function normalizeWorkCompare_(value) {
  return String(value || '')
    .replace(/[«»]/g, '"')
    .replace(/\s+/g, ' ')
    .replace(/ё/g, 'е')
    .trim()
    .toLowerCase();
}

function applyWorkStatusUpdateFromUpdateSheet_(ss, src, row, sheet) {
  const updateSheetName = src === 'kbu' ? SHEET_WORK_STATUSES_KBU_UPDATE : SHEET_WORK_STATUSES_TEKREM_UPDATE;
  const updateSheet = ss.getSheetByName(updateSheetName);
  if (!updateSheet) throw new Error('Лист "' + updateSheetName + '" не найден.');
  const executorInfo = readWorkStatusExecutors_(ss.getSheetByName(SHEET_WORK_EXECUTORS));
  const updateMap = buildWorkStatusUpdateMap_(updateSheet, src);
  const baseItem = src === 'kbu'
    ? readSingleWorkStatusKbuItem_(sheet, row, executorInfo.map)
    : readSingleWorkStatusTekRemItem_(sheet, row, executorInfo.map);
  if (!baseItem) throw new Error('Не удалось прочитать строку объекта для актуализации.');
  const update = updateMap[makeWorkStatusKey_(baseItem)];
  if (!update) throw new Error('Объект не найден на листе обновления. Проверьте ID ODX или наименование объекта.');
  const targetStatus = update.status || '';
  const targetIsCompleted = isCompletedWorkStatusValue_(targetStatus);
  const targetRequiresResourceUpdate = isResourceWorkStatusValue_(targetStatus);
  if (src === 'kbu') {
    sheet.getRange(row, 5).setValue(updateSheet.getRange(update.updateRowNumber, 5).getValue());  // Исполнитель
    sheet.getRange(row, 6).setValue(updateSheet.getRange(update.updateRowNumber, 6).getValue());  // Дата начала СМР
    if (targetIsCompleted) {
      sheet.getRange(row, 7).setValue(updateSheet.getRange(update.updateRowNumber, 7).getValue());  // Дата окончания СМР
    }
    sheet.getRange(row, 8).setValue(updateSheet.getRange(update.updateRowNumber, 8).getValue());  // Статус объекта
    if (targetRequiresResourceUpdate) {
      sheet.getRange(row, 9).setValue(updateSheet.getRange(update.updateRowNumber, 9).getValue());  // Количество людей
      sheet.getRange(row, 10).setValue(updateSheet.getRange(update.updateRowNumber, 10).getValue()); // Количество техники
    }
  } else {
    sheet.getRange(row, 2).setValue(updateSheet.getRange(update.updateRowNumber, 2).getValue());  // Исполнитель
    sheet.getRange(row, 6).setValue(updateSheet.getRange(update.updateRowNumber, 6).getValue());  // Статус объекта
    sheet.getRange(row, 7).setValue(updateSheet.getRange(update.updateRowNumber, 7).getValue());  // Дата начала СМР
    if (targetIsCompleted) {
      sheet.getRange(row, 8).setValue(updateSheet.getRange(update.updateRowNumber, 8).getValue());  // Дата окончания СМР
    }
    if (targetRequiresResourceUpdate) {
      sheet.getRange(row, 9).setValue(updateSheet.getRange(update.updateRowNumber, 9).getValue());  // Количество людей
      sheet.getRange(row, 10).setValue(updateSheet.getRange(update.updateRowNumber, 10).getValue()); // Количество техники
    }
  }
  return update;
}

function readSingleWorkStatusKbuItem_(sheet, row, executorMap) {
  if (!sheet || row < 2 || row > sheet.getLastRow()) return null;
  const r = sheet.getRange(row, 1, 1, Math.max(10, sheet.getLastColumn())).getDisplayValues()[0];
  const executor = String(r[4] || '').trim();
  const info = findWorkExecutorInfo_(executorMap, executor);
  return {
    source: 'kbu',
    sourceLabel: 'КБУ',
    rowNumber: row,
    idOdx: String(r[0] || '').trim(),
    streetName: String(r[1] || '').trim(),
    objectName: String(r[2] || '').trim(),
    district: String(r[3] || '').trim(),
    executor: executor,
    startDate: String(r[5] || '').trim(),
    endDate: String(r[6] || '').trim(),
    status: String(r[7] || '').trim(),
    peopleCount: String(r[8] || '').trim(),
    vehiclesCount: String(r[9] || '').trim(),
    contractDate: info.contractDate || '',
    inn: info.inn || ''
  };
}

function readSingleWorkStatusTekRemItem_(sheet, row, executorMap) {
  if (!sheet || row < 2 || row > sheet.getLastRow()) return null;
  const r = sheet.getRange(row, 1, 1, Math.max(10, sheet.getLastColumn())).getDisplayValues()[0];
  const executor = String(r[1] || '').trim();
  const info = findWorkExecutorInfo_(executorMap, executor);
  return {
    source: 'tekrem',
    sourceLabel: 'ТекРем',
    rowNumber: row,
    program: String(r[0] || '').replace(/\s+/g, ' ').trim(),
    executor: executor,
    idOdx: String(r[2] || '').trim(),
    streetName: String(r[3] || '').trim(),
    objectName: String(r[4] || '').trim(),
    status: String(r[5] || '').trim(),
    startDate: String(r[6] || '').trim(),
    endDate: String(r[7] || '').trim(),
    district: '',
    peopleCount: String(r[8] || '').trim(),
    vehiclesCount: String(r[9] || '').trim(),
    contractDate: info.contractDate || '',
    inn: info.inn || ''
  };
}

function ensureWorkStatusActualizationColumn_(sheet, fallbackCol) {
  const targetCol = Number(fallbackCol) || 11;
  const lastCol = Math.max(sheet.getLastColumn(), targetCol);
  const headers = sheet.getRange(1, 1, 1, lastCol).getDisplayValues()[0];
  const headerNorm = normalizeWeb_(WORK_STATUS_ACTUALIZATION_HEADER);
  let legacyCol = 0;

  // Важно: для ТекРем колонки I/J используются под людей и технику,
  // поэтому колонку актуализации держим после них — в K.
  for (let i = 0; i < headers.length; i++) {
    if (normalizeWeb_(headers[i]) !== headerNorm) continue;
    const col = i + 1;
    if (col >= targetCol) return col;
    legacyCol = col;
  }

  if (sheet.getMaxColumns() < targetCol) {
    sheet.insertColumnsAfter(sheet.getMaxColumns(), targetCol - sheet.getMaxColumns());
  }
  sheet.getRange(1, targetCol).setValue(WORK_STATUS_ACTUALIZATION_HEADER);

  // Если в старой версии заголовок оказался раньше нужной позиции,
  // переносим отметки актуализации в корректную колонку, не используя I/J как служебные.
  if (legacyCol && sheet.getLastRow() > 1) {
    const numRows = sheet.getLastRow() - 1;
    const oldValues = sheet.getRange(2, legacyCol, numRows, 1).getDisplayValues();
    const newValues = sheet.getRange(2, targetCol, numRows, 1).getDisplayValues();
    const merged = newValues.map((r, idx) => [String(r[0] || '').trim() || String(oldValues[idx][0] || '').trim()]);
    sheet.getRange(2, targetCol, numRows, 1).setValues(merged);
  }
  return targetCol;
}

function findWorkExecutorInfo_(executorMap, executor) {
  const key = normalizeWeb_(executor);
  return executorMap[key] || { contractDate: '', inn: '' };
}

function isWorkActualized_(value) {
  const s = String(value || '').trim().toLowerCase();
  return s === 'true' || s === 'да' || s === '1' || s === 'актуализировано' || s === 'актуализированы';
}

function updateWorkStatusActualization(source, rowNumber, checked) {
  requireAdmin_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const src = String(source || '').toLowerCase();
  const sheetName = src === 'kbu' ? SHEET_WORK_STATUSES_KBU : src === 'tekrem' ? SHEET_WORK_STATUSES_TEKREM : '';
  if (!sheetName) throw new Error('Неизвестный источник данных: ' + source);
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) throw new Error('Лист "' + sheetName + '" не найден.');
  const fallbackCol = src === 'kbu' ? 11 : 11;
  const actualCol = ensureWorkStatusActualizationColumn_(sheet, fallbackCol);
  const rows = parseWorkStatusRows_(rowNumber, sheet.getLastRow());
  if (!rows.length) throw new Error('Некорректная строка для обновления: ' + rowNumber);

  let appliedUpdate = false;
  const errors = [];
  rows.forEach(row => {
    try {
      if (checked) {
        applyWorkStatusUpdateFromUpdateSheet_(ss, src, row, sheet);
        appliedUpdate = true;
      }
      sheet.getRange(row, actualCol).setValue(checked ? 'Да' : 'Нет');
    } catch (e) {
      errors.push('Строка ' + row + ': ' + (e && e.message ? e.message : String(e)));
    }
  });
  if (errors.length) throw new Error(errors.join('\n'));
  logPlatformChange_('workStatuses', 'actualization', src + ':' + rows.join(','), {
    source: src,
    rowNumbers: rows,
    actualization: !!checked,
    appliedUpdate: appliedUpdate
  });
  return { success: true, source: src, rowNumbers: rows, actualization: !!checked, appliedUpdate: appliedUpdate };
}

function parseWorkStatusRows_(rowNumber, lastRow) {
  const raw = Array.isArray(rowNumber) ? rowNumber : String(rowNumber || '').split(',');
  return uniqueWorkArray_(raw.map(v => Number(String(v).replace(/[^0-9]/g, ''))))
    .filter(row => row >= 2 && row <= lastRow)
    .sort((a,b) => a - b);
}

/*************** ЗАДАЧИ ***************/
const TASKS_SHEET_NAME = 'Задачи';
const TASKS_HEADERS = [
  'ID задачи','Название задачи','Текст задачи','Ответственные Email','Ответственные ФИО',
  'Автор Email','Автор ФИО','Дата создания','Дедлайн','Статус задачи','Тип задачи',
  'Выполнена','Дата закрытия','Комментарий','Напоминание отправлено','Просрочка зафиксирована'
];
const TASK_STATUS_ACTIVE = 'Активна';
const TASK_STATUS_SOON = 'Скоро дедлайн';
const TASK_STATUS_OVERDUE = 'Просрочена';
const TASK_STATUS_DONE = 'Выполнена';

function getTasksModuleData() {
  const user = requireActiveUser_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const users = getTaskUsersForSelect_(ss);
  ensureStatusReminderTaskForToday_(ss, user);
  const sheet = getOrCreateTasksSheet_(ss);
  updateTaskStatusesInSheet_(sheet, false);
  return {
    currentUser: user,
    users: users,
    tasks: readTasks_(sheet)
  };
}

function saveTask(payload) {
  const user = requireAdmin_();
  payload = payload || {};
  const title = String(payload.title || '').trim();
  if (!title) throw new Error('Укажите название задачи.');
  const deadline = String(payload.deadline || '').trim();
  if (!deadline) throw new Error('Укажите дедлайн задачи.');

  const responsibleEmails = normalizeTaskEmailList_(payload.responsibleEmails || []);
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = getOrCreateTasksSheet_(ss);
  const users = getTaskUsersForSelect_(ss);
  const names = responsibleEmails.map(email => {
    const found = users.find(u => normalizeEmail_(u.email) === normalizeEmail_(email));
    return found ? found.fullName : email;
  }).filter(Boolean);

  const id = String(payload.id || '').trim() || makeTaskId_();
  const now = new Date();
  const values = sheet.getDataRange().getValues();
  const row = [
    id,
    title,
    String(payload.text || '').trim(),
    responsibleEmails.join(', '),
    names.join(', '),
    user.email,
    user.fullName || user.email,
    now,
    parseTaskDate_(deadline),
    TASK_STATUS_ACTIVE,
    String(payload.type || 'Другое').trim() || 'Другое',
    'Нет',
    '',
    String(payload.comment || '').trim(),
    'Нет',
    'Нет'
  ];

  let targetRow = 0;
  for (let i = 1; i < values.length; i++) {
    if (String(values[i][0]) === id) { targetRow = i + 1; break; }
  }
  if (targetRow) {
    const oldCreated = values[targetRow - 1][7] || now;
    const oldClosed = values[targetRow - 1][12] || '';
    const oldDone = String(values[targetRow - 1][11] || 'Нет');
    row[7] = oldCreated;
    row[11] = oldDone;
    row[12] = oldClosed;
    if (isTaskCompleted_(oldDone)) row[9] = TASK_STATUS_DONE;
    sheet.getRange(targetRow, 1, 1, TASKS_HEADERS.length).setValues([row]);
  } else {
    sheet.appendRow(row);
  }
  updateTaskStatusesInSheet_(sheet, false);
  logPlatformChange_('tasks', targetRow ? 'saveTask' : 'createTask', id, {
    id: id,
    title: row[1],
    text: row[2],
    responsibleEmails: responsibleEmails,
    responsibleNames: names,
    authorEmail: row[5],
    authorName: row[6],
    createdAt: row[7] instanceof Date ? row[7].toISOString() : String(row[7] || ''),
    deadline: row[8] instanceof Date ? row[8].toISOString() : String(row[8] || ''),
    status: row[9],
    type: row[10],
    completed: isTaskCompleted_(row[11]),
    closedAt: row[12] instanceof Date ? row[12].toISOString() : String(row[12] || ''),
    comment: row[13]
  });
  return { success: true, id: id };
}

function updateTaskAssignees(payload) {
  requireAdmin_();
  payload = payload || {};
  const id = String(payload.id || '').trim();
  if (!id) throw new Error('Не указан ID задачи.');
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = getOrCreateTasksSheet_(ss);
  const row = findTaskRowById_(sheet, id);
  if (!row) throw new Error('Задача не найдена.');
  const responsibleEmails = normalizeTaskEmailList_(payload.responsibleEmails || []);
  const users = getTaskUsersForSelect_(ss);
  const names = responsibleEmails.map(email => {
    const found = users.find(u => normalizeEmail_(u.email) === normalizeEmail_(email));
    return found ? found.fullName : email;
  }).filter(Boolean);
  sheet.getRange(row, 4).setValue(responsibleEmails.join(', '));
  sheet.getRange(row, 5).setValue(names.join(', '));
  logPlatformChange_('tasks', 'updateAssignees', id, {
    id: id,
    responsibleEmails: responsibleEmails,
    responsibleNames: names
  });
  return { success: true };
}

function closeTask(taskId) {
  requireAdmin_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = getOrCreateTasksSheet_(ss);
  const row = findTaskRowById_(sheet, taskId);
  if (!row) throw new Error('Задача не найдена.');
  sheet.getRange(row, 10).setValue(TASK_STATUS_DONE);
  sheet.getRange(row, 12).setValue('Да');
  const closedAt = new Date();
  sheet.getRange(row, 13).setValue(closedAt);
  logPlatformChange_('tasks', 'closeTask', taskId, {
    id: String(taskId || ''),
    completed: true,
    status: TASK_STATUS_DONE,
    closedAt: closedAt.toISOString()
  });
  return { success: true };
}

function reopenTask(taskId) {
  requireAdmin_();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = getOrCreateTasksSheet_(ss);
  const row = findTaskRowById_(sheet, taskId);
  if (!row) throw new Error('Задача не найдена.');
  sheet.getRange(row, 12).setValue('Нет');
  sheet.getRange(row, 13).setValue('');
  updateTaskStatusesInSheet_(sheet, false);
  logPlatformChange_('tasks', 'reopenTask', taskId, {
    id: String(taskId || ''),
    completed: false,
    status: TASK_STATUS_ACTIVE,
    closedAt: ''
  });
  return { success: true };
}

function checkTasksAndSendNotifications() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = getOrCreateTasksSheet_(ss);
  const changed = updateTaskStatusesInSheet_(sheet, true);
  ensureStatusReminderTaskForToday_(ss, { email: 'system', fullName: 'Система' });
  return { success: true, changed: changed };
}

function installTaskTriggers() {
  requireAdmin_();
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(t => {
    if (t.getHandlerFunction && t.getHandlerFunction() === 'checkTasksAndSendNotifications') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('checkTasksAndSendNotifications').timeBased().everyDays(1).atHour(9).create();
  return { success: true, message: 'Триггер проверки задач создан. Проверка будет выполняться ежедневно утром.' };
}

function getOrCreateTasksSheet_(ss) {
  let sheet = ss.getSheetByName(TASKS_SHEET_NAME);
  if (!sheet) sheet = ss.insertSheet(TASKS_SHEET_NAME);
  if (sheet.getLastRow() === 0 || !String(sheet.getRange(1, 1).getValue() || '').trim()) {
    sheet.getRange(1, 1, 1, TASKS_HEADERS.length).setValues([TASKS_HEADERS]);
    sheet.getRange(1, 1, 1, TASKS_HEADERS.length).setFontWeight('bold').setBackground('#f1efff');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function getTaskUsersForSelect_(ss) {
  const sheet = getOrCreateUsersSheet_(ss, getActiveUserEmail_());
  const values = sheet.getDataRange().getDisplayValues();
  return values.slice(1).filter(r => r[0] && normalizeWeb_(r[5] || USER_STATUS_ACTIVE) === normalizeWeb_(USER_STATUS_ACTIVE)).map(r => ({
    email: String(r[0] || '').trim(),
    fullName: String(r[1] || r[0] || '').trim(),
    position: String(r[2] || '').trim(),
    department: String(r[3] || '').trim(),
    role: normalizeUserRole_(r[4])
  }));
}

function readTasks_(sheet) {
  const values = sheet.getDataRange().getDisplayValues();
  if (values.length < 2) return [];
  const raw = sheet.getDataRange().getValues();
  return values.slice(1).filter(r => r[0]).map((r, idx) => {
    const rawRow = raw[idx + 1];
    const deadlineDate = rawRow[8] instanceof Date ? rawRow[8] : parseTaskDate_(r[8]);
    const status = computeTaskStatus_(deadlineDate, r[11], r[9]);
    return {
      rowNumber: idx + 2,
      id: String(r[0] || '').trim(),
      title: String(r[1] || '').trim(),
      text: String(r[2] || '').trim(),
      responsibleEmails: splitTaskList_(r[3]),
      responsibleNames: splitTaskList_(r[4]),
      authorEmail: String(r[5] || '').trim(),
      authorName: String(r[6] || '').trim(),
      createdAt: String(r[7] || '').trim(),
      deadline: String(r[8] || '').trim(),
      status: status,
      type: String(r[10] || '').trim() || 'Другое',
      completed: isTaskCompleted_(r[11]),
      closedAt: String(r[12] || '').trim(),
      comment: String(r[13] || '').trim(),
      reminderSent: String(r[14] || '').trim(),
      overdueFixed: String(r[15] || '').trim(),
      daysOverdue: getTaskDaysOverdue_(deadlineDate, r[11]),
      hoursLeft: getTaskHoursLeft_(deadlineDate, r[11])
    };
  });
}

function updateTaskStatusesInSheet_(sheet, sendEmails) {
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) return 0;
  let changed = 0;
  const now = new Date();
  for (let i = 1; i < values.length; i++) {
    const row = values[i];
    if (!row[0]) continue;
    const completed = isTaskCompleted_(row[11]);
    const deadline = row[8] instanceof Date ? row[8] : parseTaskDate_(row[8]);
    const oldStatus = String(row[9] || '').trim();
    const newStatus = computeTaskStatus_(deadline, row[11], oldStatus);
    if (oldStatus !== newStatus) {
      sheet.getRange(i + 1, 10).setValue(newStatus);
      changed++;
    }
    if (!completed && deadline && deadline instanceof Date && !isNaN(deadline.getTime())) {
      const hoursLeft = (deadline.getTime() - now.getTime()) / 36e5;
      const reminderSent = normalizeWeb_(row[14]) === normalizeWeb_('Да');
      const overdueFixed = normalizeWeb_(row[15]) === normalizeWeb_('Да');
      if (sendEmails && hoursLeft <= 24 && hoursLeft > 0 && !reminderSent) {
        sendTaskEmail_(row, 'Срок задачи подходит к концу', 'До дедлайна осталось менее 24 часов.');
        sheet.getRange(i + 1, 15).setValue('Да');
      }
      if (sendEmails && hoursLeft <= 0 && !overdueFixed) {
        sendTaskEmail_(row, 'Задача просрочена', 'Срок выполнения задачи истек.');
        sheet.getRange(i + 1, 16).setValue('Да');
      }
    }
  }
  return changed;
}

function computeTaskStatus_(deadline, completedValue, oldStatus) {
  if (isTaskCompleted_(completedValue)) return TASK_STATUS_DONE;
  if (!(deadline instanceof Date) || isNaN(deadline.getTime())) return oldStatus || TASK_STATUS_ACTIVE;
  const hoursLeft = (deadline.getTime() - new Date().getTime()) / 36e5;
  if (hoursLeft <= 0) return TASK_STATUS_OVERDUE;
  if (hoursLeft <= 24) return TASK_STATUS_SOON;
  return TASK_STATUS_ACTIVE;
}

function ensureStatusReminderTaskForToday_(ss, user) {
  const now = new Date();
  const day = now.getDay(); // 2 вторник, 4 четверг
  if (day !== 2 && day !== 4) return;
  const dateKey = Utilities.formatDate(now, Session.getScriptTimeZone(), 'yyyy-MM-dd');
  const id = 'STATUS-' + dateKey;
  const sheet = getOrCreateTasksSheet_(ss);
  if (findTaskRowById_(sheet, id)) return;
  const deadline = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 18, 0, 0);
  sheet.appendRow([
    id,
    'Актуализировать статусы работ',
    'Необходимо проверить и актуализировать данные в окне «Статусы работ». Напоминание создается автоматически каждый вторник и четверг.',
    '',
    '',
    user.email || 'system',
    user.fullName || 'Система',
    now,
    deadline,
    TASK_STATUS_ACTIVE,
    'Статусы работ',
    'Нет',
    '',
    'Автоматическое напоминание по регламентной актуализации статусов.',
    'Нет',
    'Нет'
  ]);
}

function findTaskRowById_(sheet, id) {
  if (sheet.getLastRow() < 2) return 0;
  const values = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues();
  for (let i = 0; i < values.length; i++) {
    if (String(values[i][0]) === String(id)) return i + 2;
  }
  return 0;
}

function makeTaskId_() {
  return 'TASK-' + Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyyMMdd-HHmmss') + '-' + Math.floor(Math.random() * 10000);
}

function parseTaskDate_(value) {
  if (value instanceof Date) return value;
  const s = String(value || '').trim();
  if (!s) return '';
  const normalized = s.replace('T', ' ');
  const direct = new Date(normalized);
  if (!isNaN(direct.getTime())) return direct;
  const m = s.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})(?:\s+(\d{1,2}):(\d{2}))?/);
  if (m) return new Date(Number(m[3]), Number(m[2]) - 1, Number(m[1]), Number(m[4] || 18), Number(m[5] || 0), 0);
  throw new Error('Некорректный формат дедлайна: ' + s);
}

function normalizeTaskEmailList_(list) {
  if (typeof list === 'string') list = list.split(',');
  return (list || []).map(x => normalizeEmail_(x)).filter(Boolean).filter((x, i, a) => a.indexOf(x) === i);
}

function splitTaskList_(value) {
  return String(value || '').split(',').map(x => x.trim()).filter(Boolean);
}

function isTaskCompleted_(value) {
  const s = String(value || '').trim().toLowerCase();
  return s === 'да' || s === 'true' || s === '1' || s === 'выполнена' || s === TASK_STATUS_DONE.toLowerCase();
}

function getTaskDaysOverdue_(deadline, completedValue) {
  if (isTaskCompleted_(completedValue) || !(deadline instanceof Date) || isNaN(deadline.getTime())) return 0;
  const diff = new Date().getTime() - deadline.getTime();
  return diff > 0 ? Math.ceil(diff / 86400000) : 0;
}

function getTaskHoursLeft_(deadline, completedValue) {
  if (isTaskCompleted_(completedValue) || !(deadline instanceof Date) || isNaN(deadline.getTime())) return '';
  return Math.round((deadline.getTime() - new Date().getTime()) / 36e5);
}

function sendTaskEmail_(row, subjectPrefix, text) {
  const emails = splitTaskList_(row[3]);
  if (!emails.length) return;
  const title = String(row[1] || 'Задача');
  const deadline = row[8] instanceof Date ? Utilities.formatDate(row[8], Session.getScriptTimeZone(), 'dd.MM.yyyy HH:mm') : String(row[8] || '');
  const body = text + '\n\nЗадача: ' + title + '\nДедлайн: ' + deadline + '\n\nОткройте платформу для просмотра деталей.';
  try {
    MailApp.sendEmail(emails.join(','), subjectPrefix + ': ' + title, body);
  } catch (e) {
    // Не прерываем ежедневную проверку, если отправка письма недоступна по квоте или правам.
  }
}

/*************** СОЗДАНИЕ КАРТОЧЕК ПО ТИТУЛУ ***************/
const TITLE_LOAD_STATUS_HEADER = 'Статус загрузки';
const TITLE_LOAD_STATUS_VERSION = 'Создана новая версия карточки ОДХ';
const TITLE_LOAD_STATUS_NEW = 'Создана новая карточка';
const TITLE_LOAD_STATUS_UNABLE = 'Карточка не создана';
const TITLE_UNABLE_REASON_HEADER = 'Причина невозможности создания';
const TITLE_UNABLE_REASONS = ['Нет ID ODH в СОК', 'Некорректные связи', 'Иная причина'];
const TITLE_AVAILABLE_YEARS = [2026, 2027, 2028, 2029];

function normalizeTitleYear_(year) {
  const y = Number(year) || 2026;
  return TITLE_AVAILABLE_YEARS.indexOf(y) !== -1 ? y : 2026;
}

function getTitleYearConfigs_(year) {
  year = normalizeTitleYear_(year);
  return {
    year: year,
    kbu: {
      source: 'KBU', sourceLabel: 'КБУ ' + year + ' СМР', year: year,
      baseSheet: 'Титул_КБУ' + year + '_СМР', updateSheet: 'Титул_КБУ' + year + '_СМР_обновление',
      keyType: 'street', fixedCols: 18, statusCol: 19,
      keyIndex: 1, objectIndex: 2, idIndex: 0, yearIndex: 3,
      sumStart: 4, sumEnd: 17
    },
    tr: {
      source: 'TR', sourceLabel: 'ТекРем ' + year, year: year,
      baseSheet: 'Титул_ТекРем' + year, updateSheet: 'Титул_ТекРем' + year + '_обновление',
      keyType: 'object', fixedCols: 11, statusCol: 12,
      keyIndex: 0, objectIndex: 0, idIndex: 1, yearIndex: 2,
      sumStart: 3, sumEnd: 10
    }
  };
}

function getTitleCardsModuleData(year) {
  requireActiveUser_();
  year = normalizeTitleYear_(year);
  const cfgs = getTitleYearConfigs_(year);
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const titleHelper = getTitleHelperDataForYear_(ss, year, cfgs);
  const kbu = buildTitleComparisonForConfig_(ss, cfgs.kbu, titleHelper.KBU);
  const tr = buildTitleComparisonForConfig_(ss, cfgs.tr, titleHelper.TR);
  const items = kbu.concat(tr);
  return {
    year: year,
    availableYears: TITLE_AVAILABLE_YEARS,
    items: items,
    counts: getTitleStateCounts_(items),
    statuses: [TITLE_LOAD_STATUS_VERSION, TITLE_LOAD_STATUS_NEW, TITLE_LOAD_STATUS_UNABLE],
    titleHelper: titleHelper
  };
}

function getTitleHelperDataForYear_(ss, year, cfgs) {
  const empty = {sheetName:'', fields:[], units:[], unitsMap:{}};
  const result = {KBU: Object.assign({}, empty), TR: Object.assign({}, empty)};
  const sheet = ss.getSheetByName('Титул_вспомогательное');
  if (!sheet) {
    result.KBU.sheetName = cfgs.kbu.updateSheet;
    result.TR.sheetName = cfgs.tr.updateSheet;
    return result;
  }

  const lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    result.KBU.sheetName = cfgs.kbu.updateSheet;
    result.TR.sheetName = cfgs.tr.updateSheet;
    return result;
  }

  const lastCol = Math.max(sheet.getLastColumn(), 18);
  const values = sheet.getRange(1, 1, lastRow, lastCol).getDisplayValues();
  const staticLabels = [
    'Тип документа',
    'Номер документа',
    'Дата документа',
    'Обсуждение c жителями',
    'Заказчик по СМР',
    'Характер проведения работ СМР',
    'Запланированная дата начала работ',
    'Запланированная дата окончания работ',
    'Статус экспертизы СМР',
    'Планируемая дата объявления торгов на СМР',
    'Планируемая дата заключения контракта на СМР',
    'Этап*',
    'Источник финансирования*',
    'КБК'
  ];
  const targets = [
    {source:'KBU', sheetName: cfgs.kbu.updateSheet},
    {source:'TR', sheetName: cfgs.tr.updateSheet}
  ];

  // Единицы измерения в листе «Титул_вспомогательное» являются общим справочником:
  // Q — вид работ, R — единица измерения. Они могут быть заполнены только один раз
  // в верхней части листа и не обязаны повторяться для каждого значения в столбце A.
  // Поэтому сначала собираем глобальный справочник Q:R, а затем добавляем его к каждому типу титула.
  const globalUnitsMap = {};
  const globalUnits = [];
  for (let r = 1; r < values.length; r++) {
    const workType = String(values[r][16] || '').trim();
    const unit = String(values[r][17] || '').trim();
    if (!workType || !unit) continue;
    const key = makeTitleWorkUnitKey_(workType);
    if (key && !globalUnitsMap[key]) {
      globalUnitsMap[key] = unit;
      globalUnits.push({workType: workType, unit: unit});
    }
  }

  targets.forEach(target => {
    const helper = {sheetName: target.sheetName, fields: [], units: globalUnits.slice(), unitsMap: Object.assign({}, globalUnitsMap)};
    const staticValues = new Array(staticLabels.length).fill('');
    let activeSheetName = '';

    for (let r = 1; r < values.length; r++) {
      const row = values[r];
      const rowSheet = String(row[0] || '').trim();
      // Статичные поля B:O привязаны к конкретному листу в столбце A.
      // Если A заполнен только в первой строке блока, используем последнее заполненное значение.
      if (rowSheet) activeSheetName = rowSheet;
      if (normalizeWeb_(activeSheetName) !== normalizeWeb_(target.sheetName)) continue;

      for (let i = 0; i < staticLabels.length; i++) {
        const v = String(row[i + 1] || '').trim();
        if (v && !staticValues[i]) staticValues[i] = v;
      }

      // Если для конкретного блока дополнительно указаны Q:R, они дополняют общий справочник.
      const workType = String(row[16] || '').trim();
      const unit = String(row[17] || '').trim();
      if (workType && unit) {
        const key = makeTitleWorkUnitKey_(workType);
        if (key && !helper.unitsMap[key]) {
          helper.unitsMap[key] = unit;
          helper.units.push({workType: workType, unit: unit});
        }
      }
    }
    helper.fields = staticLabels.map((label, i) => ({label: label, value: staticValues[i] || '—'}));
    result[target.source] = helper;
  });
  return result;
}

function makeTitleWorkUnitKey_(value) {
  return normalizeWeb_(value)
    .replace(/[«»"'`]/g, '')
    .replace(/ё/g, 'е')
    .replace(/[^a-zа-я0-9]+/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function getDefaultTitleWorkUnitsMap_() {
  const pairs = [
    ['Ремонт покрытия асфальтобетонного проезда в рамках благоустройства территории', 'Квадратный метр'],
    ['Ремонт покрытия асфальтобетонного тротуара в рамках благоустройства территории', 'Квадратный метр'],
    ['Ремонт дорожного бортового камня в рамках благоустройства территории', 'Погонный метр'],
    ['Ремонт гранитного бортового камня в рамках благоустройства территории', 'Погонный метр'],
    ['Ремонт люка подземных коммуникаций (смотрового колодца) в рамках благоустройства территории', 'Штука'],
    ['Устройство газона в рамках благоустройства территории', 'Квадратный метр'],
    ['Выполнение работ по монтажу/демонтажу павильонов остановочных пунктов наземного городского пассажирского транспорта', 'Штука'],
    ['Ремонт опоры наружного освещения в рамках благоустройства территории', 'Штука'],
    ['Замена элемента светильника в рамках благоустройства территории', 'Штука'],
    ['Замена урны в рамках благоустройства территории', 'Штука'],
    ['Замена лавки в рамках благоустройства территории', 'Штука']
  ];
  const map = {};
  pairs.forEach(pair => {
    map[makeTitleWorkUnitKey_(pair[0])] = pair[1];
  });
  return map;
}

function getTitleWorkUnit_(helper, label) {
  const fallback = getDefaultTitleWorkUnitsMap_();
  if (!helper || !helper.unitsMap) {
    const fallbackKey = makeTitleWorkUnitKey_(label);
    return fallback[fallbackKey] || '';
  }
  const key = makeTitleWorkUnitKey_(label);
  if (helper.unitsMap[key]) return helper.unitsMap[key];
  if (fallback[key]) return fallback[key];

  // Мягкое сопоставление на случай расхождений между заголовком титула и строкой справочника:
  // лишние пробелы, скобки, сокращения, разные окончания.
  const compactKey = key.replace(/\s+/g, '');
  const unitKeys = Object.keys(helper.unitsMap);
  let found = unitKeys.find(k => {
    if (!k) return false;
    const compact = k.replace(/\s+/g, '');
    return k === key || k.includes(key) || key.includes(k) || compact === compactKey || compact.includes(compactKey) || compactKey.includes(compact);
  });
  if (found) return helper.unitsMap[found];

  // Дополнительное сопоставление по значимым словам, чтобы единицы измерения подтягивались
  // даже если в титуле длинный заголовок немного отличается от справочника.
  const keyWords = key.split(' ').filter(w => w.length > 3 && !['рамках','благоустройства','территории'].includes(w));
  found = unitKeys.find(k => {
    const words = k.split(' ').filter(w => w.length > 3 && !['рамках','благоустройства','территории'].includes(w));
    if (!words.length || !keyWords.length) return false;
    const matches = words.filter(w => keyWords.includes(w)).length;
    return matches >= Math.min(3, words.length, keyWords.length);
  });
  return found ? helper.unitsMap[found] : '';
}

function buildTitleComparisonForConfig_(ss, cfg, helper) {
  const baseSheet = ss.getSheetByName(cfg.baseSheet);
  const updateSheet = ss.getSheetByName(cfg.updateSheet);
  if (!baseSheet) return [];
  ensureTitleStatusColumn_(baseSheet, cfg);
  if (updateSheet) ensureTitleStatusColumn_(updateSheet, cfg);

  const baseGroups = readTitleGroups_(baseSheet, cfg, false, helper);
  const updateGroups = updateSheet ? readTitleGroups_(updateSheet, cfg, true, helper) : [];
  const updateByKey = {};
  updateGroups.forEach(g => updateByKey[g.key] = g);
  const baseKeys = {};
  const result = [];

  baseGroups.forEach(base => {
    baseKeys[base.key] = true;
    const upd = updateByKey[base.key];
    if (!upd) {
      base.cardState = 'exclude';
      base.cardStateLabel = 'Исключить объект';
      base.needAction = true;
      result.push(base);
      return;
    }
    const changes = compareTitleGroups_(base, upd);
    if (changes.length) {
      base.cardState = 'actualize';
      base.cardStateLabel = 'Требуется актуализация';
      base.needAction = true;
      base.changes = changes;
      base.updateValues = upd.values;
      base.updateObjects = upd.objects;
      base.updateRows = upd.rows;
      base.updateRowNumbers = upd.rowNumbers;
      result.push(base);
    } else {
      base.cardState = 'ok';
      base.cardStateLabel = 'Актуально';
      base.needAction = false;
      result.push(base);
    }
  });

  updateGroups.forEach(upd => {
    if (baseKeys[upd.key]) return;
    upd.cardState = 'create';
    upd.cardStateLabel = 'Создать новый объект';
    upd.needAction = true;
    upd.fromUpdateOnly = true;
    upd.loadStatus = upd.loadStatus || TITLE_LOAD_STATUS_NEW;
    result.push(upd);
  });
  return result;
}

function readTitleGroups_(sheet, cfg, fromUpdate, helper) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];
  const lastCol = Math.max(sheet.getLastColumn(), cfg.statusCol + 1);
  const raw = sheet.getRange(1, 1, lastRow, lastCol).getValues();
  const display = sheet.getRange(1, 1, lastRow, lastCol).getDisplayValues();
  const headers = display[0];
  const map = {};

  for (let r = 1; r < raw.length; r++) {
    const row = raw[r];
    const rowDisplay = display[r];
    const keyName = String(rowDisplay[cfg.keyIndex] || row[cfg.keyIndex] || '').trim();
    const objectName = String(rowDisplay[cfg.objectIndex] || row[cfg.objectIndex] || '').trim();
    if (!keyName && !objectName) continue;
    const key = makeTitleKey_(cfg, rowDisplay, row);
    if (!key) continue;
    if (!map[key]) {
      map[key] = {
        source: cfg.source,
        sourceLabel: cfg.sourceLabel,
        year: cfg.year || 2026,
        sheetName: sheet.getName(),
        key: key,
        title: cfg.keyType === 'street' ? keyName : objectName,
        streetName: cfg.keyType === 'street' ? keyName : '',
        objectName: cfg.keyType === 'street' ? '' : objectName,
        idOdx: String(rowDisplay[cfg.idIndex] || '').trim(),
        yearLastRepair: String(rowDisplay[cfg.yearIndex] || '').trim(),
        objects: [],
        rowNumbers: [],
        rows: [],
        values: {},
        valueLabels: {},
        valueUnits: {},
        loadStatus: String(rowDisplay[cfg.statusCol - 1] || '').trim(),
        unableReason: String(rowDisplay[cfg.statusCol] || '').trim(),
        fromUpdate: fromUpdate
      };
      for (let c = cfg.sumStart; c <= cfg.sumEnd; c++) {
        map[key].values[c] = 0;
        map[key].valueLabels[c] = headers[c] || ('Столбец ' + columnToLetter_(c + 1));
        map[key].valueUnits[c] = getTitleWorkUnit_(helper, map[key].valueLabels[c]);
      }
    }
    const g = map[key];
    g.rowNumbers.push(r + 1);
    g.rows.push(row.slice(0, cfg.fixedCols));
    const obj = String(rowDisplay[cfg.objectIndex] || row[cfg.objectIndex] || '').trim();
    if (obj && g.objects.indexOf(obj) === -1) g.objects.push(obj);
    const id = String(rowDisplay[cfg.idIndex] || '').trim();
    if (id && String(g.idOdx || '').indexOf(id) === -1) g.idOdx = g.idOdx ? (g.idOdx + ', ' + id) : id;
    const year = String(rowDisplay[cfg.yearIndex] || '').trim();
    if (year && String(g.yearLastRepair || '').indexOf(year) === -1) g.yearLastRepair = g.yearLastRepair ? (g.yearLastRepair + ', ' + year) : year;
    for (let c = cfg.sumStart; c <= cfg.sumEnd; c++) {
      g.values[c] += toTitleNumber_(row[c]);
    }
    const status = String(rowDisplay[cfg.statusCol - 1] || '').trim();
    if (status && !g.loadStatus) g.loadStatus = status;
    const unableReason = String(rowDisplay[cfg.statusCol] || '').trim();
    if (unableReason && !g.unableReason) g.unableReason = unableReason;
  }
  return Object.keys(map).map(k => {
    const g = map[k];
    Object.keys(g.values).forEach(c => g.values[c] = roundTitleNumber_(g.values[c]));
    return g;
  });
}

function makeTitleKey_(cfg, displayRow, rawRow) {
  if (cfg.keyType === 'street') {
    return cfg.source + '|' + normalizeWeb_(displayRow[cfg.keyIndex] || rawRow[cfg.keyIndex]);
  }

  const objectName = normalizeWeb_(displayRow[cfg.objectIndex] || rawRow[cfg.objectIndex]);
  const id = normalizeTitleOdhIdKey_(displayRow[cfg.idIndex] || rawRow[cfg.idIndex]);

  // Для ТекРем одна карточка ОДХ должна определяться в первую очередь по ID ODH.
  // Раньше ключ собирался как ID + наименование объекта, поэтому один и тот же ID ODH
  // при разных/уточненных наименованиях отображался двумя отдельными карточками.
  // Теперь все строки с одинаковым ID ODH группируются в одну карточку, а разные
  // наименования попадают в блок «Объекты в составе карточки». Если ID не заполнен
  // или содержит служебное значение, используем наименование объекта как запасной ключ.
  return cfg.source + '|' + (id ? ('id:' + id) : ('object:' + objectName));
}

function normalizeTitleOdhIdKey_(value) {
  const text = String(value || '').trim();
  if (!text) return '';
  const normalized = normalizeWeb_(text);
  const serviceValues = {
    '#н/д': true,
    '#n/a': true,
    'н/д': true,
    'n/a': true,
    'нет': true,
    '-': true,
    '—': true
  };
  if (serviceValues[normalized]) return '';
  return normalized
    .replace(/\.0+$/, '')
    .replace(/[^a-zа-я0-9]+/gi, '')
    .trim();
}

function compareTitleGroups_(base, upd) {
  const changes = [];
  Object.keys(base.values || {}).forEach(c => {
    const label = base.valueLabels[c] || (upd.valueLabels || {})[c] || ('Столбец ' + columnToLetter_(Number(c) + 1));
    const precision = getTitleComparePrecision_(label);
    const oldRaw = Number(base.values[c]) || 0;
    const newRaw = Number((upd.values || {})[c]) || 0;
    const oldValue = roundTitleNumberByPrecision_(oldRaw, precision);
    const newValue = roundTitleNumberByPrecision_(newRaw, precision);

    // Не считаем изменением разную разрядность одного и того же значения.
    // Например, для стоимости 4286588,68 и 4286588,677 — это одно значение
    // при рабочем сравнении до копеек, поэтому карточка не должна попадать
    // в «Требуется актуализация».
    if (!isTitleNumberEqual_(oldValue, newValue, precision)) {
      changes.push({
        field: c,
        label: label,
        oldValue: formatTitleNumberByPrecision_(oldValue, precision),
        newValue: formatTitleNumberByPrecision_(newValue, precision)
      });
    }
  });
  const oldObjects = (base.objects || []).join(' | ');
  const newObjects = (upd.objects || []).join(' | ');
  if (normalizeWeb_(oldObjects) !== normalizeWeb_(newObjects)) {
    changes.push({field:'objects', label:'Состав объектов', oldValue:oldObjects || '—', newValue:newObjects || '—'});
  }
  return changes;
}

function saveTitleCardLoadStatus(payload) {
  requireAdmin_();
  payload = payload || {};
  const cfg = getTitleConfigBySource_(payload.source, payload.year);
  const status = normalizeTitleLoadStatus_(payload.loadStatus);
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = ss.getSheetByName(payload.fromUpdateOnly ? cfg.updateSheet : cfg.baseSheet) || ss.getSheetByName(cfg.baseSheet);
  if (!sheet) throw new Error('Лист для сохранения статуса не найден.');
  ensureTitleStatusColumn_(sheet, cfg);
  const groups = readTitleGroups_(sheet, cfg, !!payload.fromUpdateOnly);
  const group = groups.find(g => g.key === payload.key);
  if (!group) throw new Error('Карточка не найдена для сохранения статуса.');
  setTitleGroupStatus_(sheet, cfg, group, status, payload.unableReason || group.unableReason || '');
  logPlatformChange_('titleCards', 'loadStatus', cfg.source + ':' + group.key, {
    year: normalizeTitleYear_(payload.year),
    source: cfg.source,
    key: group.key,
    loadStatus: status,
    unableReason: payload.unableReason || group.unableReason || ''
  });
  return {success:true, status:status};
}

function applyTitleCardAction(payload) {
  const user = requireAdmin_();
  payload = payload || {};
  const cfg = getTitleConfigBySource_(payload.source, payload.year);
  const action = String(payload.action || '').trim();
  const loadStatus = normalizeTitleLoadStatus_(payload.loadStatus || (action === 'create' ? TITLE_LOAD_STATUS_NEW : TITLE_LOAD_STATUS_VERSION));
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  // Важно: readTitleGroups_ в этой версии принимает helper для подтягивания единиц измерения.
  // Раньше здесь переменная helper не создавалась, из-за чего при нажатии
  // «Создать новый объект» возникала ошибка: ReferenceError: helper is not defined.
  const cfgs = getTitleYearConfigs_(payload.year);
  const titleHelper = getTitleHelperDataForYear_(ss, normalizeTitleYear_(payload.year), cfgs);
  const helper = cfg.source === 'KBU' ? titleHelper.KBU : titleHelper.TR;

  const baseSheet = ss.getSheetByName(cfg.baseSheet);
  const updateSheet = ss.getSheetByName(cfg.updateSheet);
  if (!baseSheet) throw new Error('Лист "' + cfg.baseSheet + '" не найден.');
  ensureTitleStatusColumn_(baseSheet, cfg);
  if (updateSheet) ensureTitleStatusColumn_(updateSheet, cfg);

  const baseGroups = readTitleGroups_(baseSheet, cfg, false, helper);
  const updateGroups = updateSheet ? readTitleGroups_(updateSheet, cfg, true, helper) : [];
  const baseGroup = baseGroups.find(g => g.key === payload.key);
  const updateGroup = updateGroups.find(g => g.key === payload.key);

  if (action === 'exclude') {
    if (!baseGroup) throw new Error('Объект для исключения не найден в основном листе.');
    deleteRowsDescending_(baseSheet, baseGroup.rowNumbers);
    logTitleAction_(user, cfg.sourceLabel, 'Исключить объект', baseGroup.title, '', '');
    logPlatformChange_('titleCards', 'action', cfg.source + ':' + baseGroup.key, {
      year: normalizeTitleYear_(payload.year),
      source: cfg.source,
      key: baseGroup.key,
      action: action,
      loadStatus: '',
      title: baseGroup.title
    });
    return {success:true, message:'Объект исключен из основного листа.'};
  }

  if (action === 'actualize') {
    if (!baseGroup) throw new Error('Объект для актуализации не найден в основном листе.');
    if (!updateGroup) throw new Error('Объект не найден на листе обновления.');
    deleteRowsDescending_(baseSheet, baseGroup.rowNumbers);
    appendTitleRows_(baseSheet, cfg, updateGroup.rows, loadStatus);
    logTitleAction_(user, cfg.sourceLabel, 'Актуализировать объект', updateGroup.title, '', loadStatus);
    logPlatformChange_('titleCards', 'action', cfg.source + ':' + updateGroup.key, {
      year: normalizeTitleYear_(payload.year),
      source: cfg.source,
      key: updateGroup.key,
      action: action,
      loadStatus: loadStatus,
      title: updateGroup.title
    });
    return {success:true, message:'Объект актуализирован по листу обновления.'};
  }

  if (action === 'unableCreate') {
    const reason = normalizeTitleUnableReason_(payload.unableReason);
    if (baseGroup) {
      setTitleGroupStatus_(baseSheet, cfg, baseGroup, TITLE_LOAD_STATUS_UNABLE, reason);
      logTitleAction_(user, cfg.sourceLabel, 'Невозможно создать карточку в СОК', baseGroup.title, '', reason);
      logPlatformChange_('titleCards', 'action', cfg.source + ':' + baseGroup.key, {
        year: normalizeTitleYear_(payload.year),
        source: cfg.source,
        key: baseGroup.key,
        action: action,
        loadStatus: TITLE_LOAD_STATUS_UNABLE,
        unableReason: reason,
        title: baseGroup.title
      });
      return {success:true, message:'Карточка отмечена как не созданная.'};
    }
    if (!updateGroup) throw new Error('Карточка не найдена на листе обновления для переноса в основной титул.');
    appendTitleRows_(baseSheet, cfg, updateGroup.rows, TITLE_LOAD_STATUS_UNABLE, reason);
    logTitleAction_(user, cfg.sourceLabel, 'Невозможно создать карточку в СОК', updateGroup.title, '', reason);
    logPlatformChange_('titleCards', 'action', cfg.source + ':' + updateGroup.key, {
      year: normalizeTitleYear_(payload.year),
      source: cfg.source,
      key: updateGroup.key,
      action: action,
      loadStatus: TITLE_LOAD_STATUS_UNABLE,
      unableReason: reason,
      title: updateGroup.title
    });
    return {success:true, message:'Карточка перенесена в основной титул со статусом «Карточка не создана».'};
  }

  if (action === 'create') {
    if (!updateGroup) throw new Error('Новый объект не найден на листе обновления.');
    appendTitleRows_(baseSheet, cfg, updateGroup.rows, loadStatus);
    logTitleAction_(user, cfg.sourceLabel, 'Создать новый объект', updateGroup.title, '', loadStatus);
    logPlatformChange_('titleCards', 'action', cfg.source + ':' + updateGroup.key, {
      year: normalizeTitleYear_(payload.year),
      source: cfg.source,
      key: updateGroup.key,
      action: action,
      loadStatus: loadStatus,
      title: updateGroup.title
    });
    return {success:true, message:'Новый объект создан в основном листе.'};
  }

  throw new Error('Неизвестное действие с карточкой титула.');
}

function appendTitleRows_(sheet, cfg, rows, loadStatus, unableReason) {
  if (!rows || !rows.length) return;
  ensureTitleStatusColumn_(sheet, cfg);
  const finalStatus = normalizeTitleLoadStatus_(loadStatus);
  const finalReason = finalStatus === TITLE_LOAD_STATUS_UNABLE ? normalizeTitleUnableReason_(unableReason) : '';
  const lastCol = cfg.statusCol + 1;
  const data = rows.map(r => {
    const out = r.slice(0, cfg.fixedCols);
    while (out.length < cfg.statusCol - 1) out.push('');
    out[cfg.statusCol - 1] = finalStatus;
    out[cfg.statusCol] = finalReason;
    return out;
  });
  sheet.getRange(sheet.getLastRow() + 1, 1, data.length, lastCol).setValues(data);
}

function deleteRowsDescending_(sheet, rowNumbers) {
  (rowNumbers || []).map(Number).filter(Boolean).sort((a,b) => b - a).forEach(row => sheet.deleteRow(row));
}



/*************** PDF ОБОСНОВАНИЕ АДРЕСНОГО ПЕРЕЧНЯ ***************/
const TITLE_JUSTIFICATION_FOLDER_NAME = 'Обоснования адресных перечней';
const TITLE_JUSTIFICATION_REASON = 'Предложение ГБУ «Автомобильные дороги»';
const TITLE_JUSTIFICATION_SIGNATURE_BASE64 = [
  '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',
  'P4LCroiC7P4ZAAAAAElFTkSuQmCC'
].join('');

/**
 * Вызывается из Index.html через google.script.run.
 * Формирует PDF обоснования адресного перечня по выбранному году и программе.
 * payload: {year: 2026|2027|2028|2029, source: 'KBU'|'TR'}
 */
function generateTitleJustificationPdf(payload) {
  requireAdmin_();
  payload = payload || {};
  const year = normalizeTitleYear_(payload.year);
  const source = String(payload.source || '').trim();
  if (source !== 'KBU' && source !== 'TR') {
    throw new Error('Неизвестная программа для документа обоснования: ' + source);
  }

  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const cfg = getTitleJustificationConfig_(source, year);
  const sheet = ss.getSheetByName(cfg.sheetName);
  if (!sheet) throw new Error('Лист "' + cfg.sheetName + '" не найден.');

  const rows = collectTitleJustificationRows_(sheet, cfg);
  if (!rows.length) {
    throw new Error('На листе "' + cfg.sheetName + '" не найдены строки для формирования документа.');
  }

  const docTitle = source === 'KBU'
    ? 'Предложение к включению в адресный перечень объектов благоустройства на ' + year + ' год'
    : 'Предложение к включению в адресный перечень объектов ремонта на ' + year + ' год';

  const fileName = 'Обоснование адресного перечня ' + (source === 'KBU' ? 'КБУ' : 'ТекРем') + ' ' + year + '.pdf';
  const doc = DocumentApp.create(fileName.replace(/\.pdf$/i, ''));
  const docId = doc.getId();

  buildTitleJustificationDocument_(doc, docTitle, rows, source);
  doc.saveAndClose();

  const pdfBlob = DriveApp.getFileById(docId).getBlob().getAs(MimeType.PDF).setName(fileName);
  const folder = getOrCreateTitleJustificationFolder_();
  const pdfFile = folder.createFile(pdfBlob);

  try {
    const docFile = DriveApp.getFileById(docId);
    folder.addFile(docFile);
    try { DriveApp.getRootFolder().removeFile(docFile); } catch (e) {}
  } catch (e) {}

  logTitleAction_(requireActiveUser_(), cfg.programLabel, 'Сформировать PDF обоснования', docTitle, '', fileName);

  return {
    success: true,
    url: pdfFile.getUrl(),
    fileName: fileName,
    count: rows.length,
    sheetName: cfg.sheetName
  };
}

function getTitleJustificationConfig_(source, year) {
  year = normalizeTitleYear_(year);
  if (source === 'KBU') {
    return {
      source: 'KBU',
      programLabel: 'КБУ ' + year + ' СМР',
      sheetName: 'Титул_КБУ' + year + '_СМР_обновление',
      districtIndex: 19, // T: Округ
      nameIndex: 1,     // B: Наименование улицы
      areaIndex: 7,     // H: Площадь благоустройства
      nameHeader: 'Наименование улицы'
    };
  }
  return {
    source: 'TR',
    programLabel: 'ТекРем ' + year,
    sheetName: 'Титул_ТекРем' + year + '_обновление',
    districtIndex: 12, // M: Округ
    nameIndex: 0,     // A: Наименование объекта
    areaIndex: 5,     // F: Площадь благоустройства
    nameHeader: 'Наименование объекта'
  };
}

function collectTitleJustificationRows_(sheet, cfg) {
  const lastRow = sheet.getLastRow();
  const lastCol = Math.max(sheet.getLastColumn(), cfg.districtIndex + 1, cfg.nameIndex + 1, cfg.areaIndex + 1);
  if (lastRow < 2) return [];

  const values = sheet.getRange(2, 1, lastRow - 1, lastCol).getValues();
  const groups = {};

  values.forEach(row => {
    const name = String(row[cfg.nameIndex] || '').trim();
    if (!name) return;

    const key = normalizeWeb_(name);
    const district = String(row[cfg.districtIndex] || '').trim();
    const area = toTitleNumber_(row[cfg.areaIndex]);

    if (!groups[key]) groups[key] = {district: district, name: name, area: 0};
    groups[key].area += area;
    if (!groups[key].district && district) groups[key].district = district;
  });

  return Object.keys(groups)
    .map(k => groups[k])
    .filter(x => x.name)
    .sort((a, b) => String(a.name).localeCompare(String(b.name), 'ru', {numeric: true, sensitivity: 'base'}));
}

function buildTitleJustificationDocument_(doc, docTitle, rows, source) {
  const body = doc.getBody();
  body.clear();

  // Формат страницы под шаблон: A4, книжная ориентация, компактная таблица.
  try {
    body.setPageWidth(595.28).setPageHeight(841.89);
    body.setMarginTop(36).setMarginBottom(34).setMarginLeft(24).setMarginRight(24);
  } catch (e) {}

  const nameHeader = source === 'KBU' ? 'Наименование улицы' : 'Наименование объекта';
  const headerRow = [
    '№ п/п',
    'Округ',
    nameHeader,
    'Площадь благоустройства, кв.м.',
    'Основание для проведения работ'
  ];

  // В Google Docs нет стабильного автоповтора первой строки таблицы при экспорте через DocumentApp,
  // поэтому делаем документ как в шаблоне: отдельная таблица на каждую страницу с повтором заголовков.
  const firstPageRows = 60;
  const nextPageRows = 72;
  let offset = 0;
  let pageIndex = 0;

  while (offset < rows.length) {
    if (pageIndex > 0) body.appendPageBreak();
    if (pageIndex === 0) {
      buildTitleJustificationHeader_(body, docTitle);
    }

    const limit = pageIndex === 0 ? firstPageRows : nextPageRows;
    const chunk = rows.slice(offset, offset + limit);
    const tableData = [headerRow];

    chunk.forEach((r, idx) => {
      tableData.push([
        String(offset + idx + 1),
        r.district || '',
        r.name || '',
        formatTitleJustificationArea_(r.area),
        TITLE_JUSTIFICATION_REASON
      ]);
    });

    const table = body.appendTable(tableData);
    styleTitleJustificationTable_(table);

    offset += chunk.length;
    pageIndex++;
  }
}

function buildTitleJustificationHeader_(body, docTitle) {
  const font = 'Times New Roman';

  const p1 = body.appendParagraph('Согласовано');
  p1.setFontFamily(font).setFontSize(13).setBold(true)
    .setAlignment(DocumentApp.HorizontalAlignment.LEFT)
    .setSpacingBefore(0).setSpacingAfter(0).setLineSpacing(1);

  const p2 = body.appendParagraph('Заместитель руководителя ГБУ "Автомобильные дороги"');
  p2.setFontFamily(font).setFontSize(11).setBold(false)
    .setAlignment(DocumentApp.HorizontalAlignment.LEFT)
    .setSpacingBefore(0).setSpacingAfter(0).setLineSpacing(1);

  // Подпись-изображение убрана: остается только строка для ручного подписания и ФИО.
  const signTable = body.appendTable([['', 'М.М. Никитаев']]);
  signTable.setBorderWidth(0);
  try {
    signTable.getRow(0).getCell(0).setWidth(330);
    signTable.getRow(0).getCell(1).setWidth(190);
  } catch (e) {}

  for (let c = 0; c < 2; c++) {
    const cell = signTable.getRow(0).getCell(c);
    cell.setPaddingTop(0).setPaddingBottom(0).setPaddingLeft(0).setPaddingRight(0);
    try { cell.setVerticalAlignment(DocumentApp.VerticalAlignment.BOTTOM); } catch (e) {}
  }

  const lineParagraph = signTable.getRow(0).getCell(0).getChild(0).asParagraph();
  lineParagraph.appendText('____________________________________________')
    .setFontFamily(font).setFontSize(10).setBold(false);
  lineParagraph.setSpacingBefore(48).setSpacingAfter(0).setAlignment(DocumentApp.HorizontalAlignment.LEFT);

  const nameParagraph = signTable.getRow(0).getCell(1).getChild(0).asParagraph();
  nameParagraph.setFontFamily(font).setFontSize(10).setBold(false)
    .setAlignment(DocumentApp.HorizontalAlignment.LEFT)
    .setSpacingBefore(48).setSpacingAfter(0);

  const spacer = body.appendParagraph('');
  spacer.setSpacingBefore(0).setSpacingAfter(14).setLineSpacing(1);

  const title = body.appendParagraph(docTitle);
  title.setAlignment(DocumentApp.HorizontalAlignment.CENTER)
    .setFontFamily(font)
    .setFontSize(11)
    .setBold(false)
    .setSpacingBefore(0)
    .setSpacingAfter(10)
    .setLineSpacing(1);
}

function styleTitleJustificationTable_(table) {
  table.setBorderWidth(0.5);
  const widths = [46, 48, 182, 78, 190];
  for (let r = 0; r < table.getNumRows(); r++) {
    const row = table.getRow(r);
    for (let c = 0; c < row.getNumCells(); c++) {
      const cell = row.getCell(c);
      try { cell.setWidth(widths[c]); } catch (e) {}

      // Не фиксируем высоту строки: Google Docs сам подбирает высоту под текст.
      cell.setPaddingTop(1).setPaddingBottom(1).setPaddingLeft(1.6).setPaddingRight(1.6);
      try { cell.setVerticalAlignment(DocumentApp.VerticalAlignment.CENTER); } catch (e) {}

      const text = cell.editAsText();
      try {
        text.setFontFamily('Times New Roman').setFontSize(6);
        if (r === 0) text.setFontSize(6).setBold(true);
        else text.setBold(false);
      } catch (e) {}

      for (let i = 0; i < cell.getNumChildren(); i++) {
        const child = cell.getChild(i);
        if (child.getType && child.getType() === DocumentApp.ElementType.PARAGRAPH) {
          const p = child.asParagraph();
          p.setSpacingBefore(0).setSpacingAfter(0).setLineSpacing(1);
          p.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
          if (r === 0) p.setBold(true);
          else p.setBold(false);
        }
      }
    }
  }
}

function formatTitleJustificationArea_(value) {
  const n = Math.round((Number(value) || 0) * 100) / 100;
  const parts = n.toFixed(2).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  return parts.join(',');
}

function getOrCreateTitleJustificationFolder_() {
  try {
    const rootFolder = DriveApp.getFolderById(ACTS_FOLDER_ID);
    return getOrCreateSubfolder_(rootFolder, TITLE_JUSTIFICATION_FOLDER_NAME);
  } catch (e) {
    return getOrCreateFolder_(TITLE_JUSTIFICATION_FOLDER_NAME);
  }
}

function getTitleStateCounts_(items) {
  const counts = {total: items.length, ok:0, actualize:0, exclude:0, create:0, needAction:0};
  items.forEach(i => {
    const state = i.cardState || 'ok';
    counts[state] = (counts[state] || 0) + 1;
    if (i.needAction) counts.needAction++;
  });
  return counts;
}

function getTitleConfigBySource_(source, year) {
  const s = String(source || '').trim();
  const cfgs = getTitleYearConfigs_(year);
  if (s === cfgs.kbu.source) return cfgs.kbu;
  if (s === cfgs.tr.source) return cfgs.tr;
  throw new Error('Неизвестный источник титула: ' + source);
}

function ensureTitleStatusColumn_(sheet, cfg) {
  const reasonCol = cfg.statusCol + 1;
  if (sheet.getMaxColumns() < reasonCol) sheet.insertColumnsAfter(sheet.getMaxColumns(), reasonCol - sheet.getMaxColumns());
  const header = String(sheet.getRange(1, cfg.statusCol).getValue() || '').trim();
  if (!header) {
    sheet.getRange(1, cfg.statusCol).setValue(TITLE_LOAD_STATUS_HEADER).setFontWeight('bold').setBackground('#f1efff');
  }
  const reasonHeader = String(sheet.getRange(1, reasonCol).getValue() || '').trim();
  if (!reasonHeader) {
    sheet.getRange(1, reasonCol).setValue(TITLE_UNABLE_REASON_HEADER).setFontWeight('bold').setBackground('#fff0f2');
  }
}

function normalizeTitleLoadStatus_(status) {
  const value = String(status || '').trim();
  if (normalizeWeb_(value) === normalizeWeb_(TITLE_LOAD_STATUS_NEW)) return TITLE_LOAD_STATUS_NEW;
  if (normalizeWeb_(value) === normalizeWeb_(TITLE_LOAD_STATUS_UNABLE)) return TITLE_LOAD_STATUS_UNABLE;
  return TITLE_LOAD_STATUS_VERSION;
}

function normalizeTitleUnableReason_(reason) {
  const value = String(reason || '').trim();
  const found = TITLE_UNABLE_REASONS.find(r => normalizeWeb_(r) === normalizeWeb_(value));
  return found || TITLE_UNABLE_REASONS[0];
}

function setTitleGroupStatus_(sheet, cfg, group, status, reason) {
  if (!group || !group.rowNumbers || !group.rowNumbers.length) return;
  ensureTitleStatusColumn_(sheet, cfg);
  const finalStatus = normalizeTitleLoadStatus_(status);
  const finalReason = finalStatus === TITLE_LOAD_STATUS_UNABLE ? normalizeTitleUnableReason_(reason) : '';
  group.rowNumbers.forEach(row => {
    sheet.getRange(row, cfg.statusCol).setValue(finalStatus);
    sheet.getRange(row, cfg.statusCol + 1).setValue(finalReason);
  });
}

function toTitleNumber_(value) {
  if (typeof value === 'number') return isFinite(value) ? value : 0;
  const s = String(value || '').replace(/\s+/g, '').replace(',', '.').replace(/[^0-9.\-]/g, '');
  const n = Number(s);
  return isFinite(n) ? n : 0;
}

function roundTitleNumber_(n) {
  return Math.round((Number(n) || 0) * 1000) / 1000;
}

function getTitleComparePrecision_(label) {
  // Для всех числовых показателей в карточках по титулу сравниваем значения
  // в рабочей точности до 2 знаков после запятой. Это убирает ложные
  // актуализации из-за разной разрядности в исходных листах:
  // 4286588,68 и 4286588,677; 28,4 и 28,395 и т.п.
  // Реальные изменения сохраняются: например, 28,40 -> 28,41 будет показано.
  return 2;
}

function roundTitleNumberByPrecision_(n, precision) {
  const p = Math.pow(10, Number(precision) || 0);
  return Math.round((Number(n) || 0) * p) / p;
}

function isTitleNumberEqual_(a, b, precision) {
  const p = Math.pow(10, Number(precision) || 0);
  return Math.abs((Number(a) || 0) - (Number(b) || 0)) < (0.5 / p);
}

function formatTitleNumberByPrecision_(n, precision) {
  const p = Number(precision);
  const value = roundTitleNumberByPrecision_(n, p);
  return String(value).replace('.', ',');
}

function formatTitleNumber_(n) {
  n = roundTitleNumber_(n);
  return String(n).replace('.', ',');
}

function columnToLetter_(column) {
  let temp = '';
  while (column > 0) {
    const rem = (column - 1) % 26;
    temp = String.fromCharCode(65 + rem) + temp;
    column = Math.floor((column - rem - 1) / 26);
  }
  return temp;
}

function logTitleAction_(user, source, action, objectName, oldValue, newValue) {
  try {
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    let sheet = ss.getSheetByName('История_действий');
    if (!sheet) sheet = ss.insertSheet('История_действий');
    if (sheet.getLastRow() === 0) sheet.appendRow(['Дата и время','Email','ФИО','Роль','Раздел','Действие','Объект','Старое значение','Новое значение']);
    sheet.appendRow([new Date(), user.email, user.fullName, user.role, 'Создание карточек по титулу / ' + source, action, objectName, oldValue, newValue]);
  } catch (e) {}
}


/*************** ФОРМИРОВАНИЕ ДОРОЖНОЙ КАРТЫ ***************/
const ROADMAP_AVAILABLE_YEARS = [2026, 2027, 2028, 2029];

function normalizeRoadmapYear_(year) {
  const y = Number(year) || 2026;
  return ROADMAP_AVAILABLE_YEARS.indexOf(y) !== -1 ? y : 2026;
}

function getRoadmapYearConfigs_(year) {
  year = normalizeRoadmapYear_(year);
  const shortYear = String(year).slice(2);
  return {
    year: year,
    kbu: {
      source: 'KBU',
      sourceLabel: 'КБУ ' + year,
      year: year,
      baseSheet: 'ДК_КБУ' + shortYear,
      updateSheet: 'ДК_КБУ' + shortYear + '_обновление',
      keyType: 'street',
      fixedCols: 5,
      idIndex: 0,
      streetIndex: 1,
      objectIndex: 2,
      areaIndex: 3,
      costIndex: 4
    },
    tr: {
      source: 'TR',
      sourceLabel: 'ТекРем ' + year,
      year: year,
      baseSheet: 'ДК_ТекРем' + year,
      updateSheet: 'ДК_ТекРем' + year + '_обновление',
      keyType: 'id',
      fixedCols: 4,
      objectIndex: 0,
      idIndex: 1,
      areaIndex: 2,
      costIndex: 3
    }
  };
}

function getRoadmapModuleData(year) {
  requireActiveUser_();
  year = normalizeRoadmapYear_(year);
  const cfgs = getRoadmapYearConfigs_(year);
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const kbu = buildRoadmapComparisonForConfig_(ss, cfgs.kbu);
  const tr = buildRoadmapComparisonForConfig_(ss, cfgs.tr);
  const items = kbu.concat(tr);
  return {
    year: year,
    availableYears: ROADMAP_AVAILABLE_YEARS,
    items: items,
    counts: getRoadmapStateCounts_(items)
  };
}

function buildRoadmapComparisonForConfig_(ss, cfg) {
  const baseSheet = ss.getSheetByName(cfg.baseSheet);
  const updateSheet = ss.getSheetByName(cfg.updateSheet);
  const baseGroups = baseSheet ? readRoadmapGroups_(baseSheet, cfg, false) : [];
  const updateGroups = updateSheet ? readRoadmapGroups_(updateSheet, cfg, true) : [];

  // Важно для ТекРем: лист обновления сначала собирается по ID ODX,
  // но сопоставление с текущей ДК выполняется по наименованию объекта,
  // потому что в текущей дорожной карте ID ODX может быть пустым.
  const updateByCompareKey = {};
  updateGroups.forEach(g => {
    if (!g.compareKey) return;
    if (!updateByCompareKey[g.compareKey]) updateByCompareKey[g.compareKey] = g;
  });

  const baseCompareKeys = {};
  const result = [];

  baseGroups.forEach(base => {
    if (base.compareKey) baseCompareKeys[base.compareKey] = true;
    const upd = updateByCompareKey[base.compareKey];
    if (!upd) {
      base.cardState = 'exclude';
      base.cardStateLabel = 'Исключить из дорожной карты';
      base.needAction = true;
      result.push(base);
      return;
    }
    const changes = compareRoadmapGroups_(base, upd);
    if (changes.length) {
      base.cardState = 'actualize';
      base.cardStateLabel = 'Требуется актуализация';
      base.needAction = true;
      base.changes = changes;
      base.updateKey = upd.key;
      base.updateRows = upd.rows;
      base.updateRowNumbers = upd.rowNumbers;
      base.updateValues = {area: upd.area, cost: upd.cost};
      base.updateObjects = upd.objects;
      base.updateIdOdx = upd.idOdx;
      result.push(base);
    } else {
      base.cardState = 'ok';
      base.cardStateLabel = 'Актуально';
      base.needAction = false;
      base.updateKey = upd.key;
      result.push(base);
    }
  });

  updateGroups.forEach(upd => {
    if (baseCompareKeys[upd.compareKey]) return;
    upd.cardState = 'create';
    upd.cardStateLabel = 'Добавить в дорожную карту';
    upd.needAction = true;
    upd.fromUpdateOnly = true;
    result.push(upd);
  });
  return result;
}

function readRoadmapGroups_(sheet, cfg, fromUpdate) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return [];
  const lastCol = Math.max(sheet.getLastColumn(), cfg.fixedCols);
  const raw = sheet.getRange(1, 1, lastRow, lastCol).getValues();
  const display = sheet.getRange(1, 1, lastRow, lastCol).getDisplayValues();
  const map = {};

  for (let r = 1; r < raw.length; r++) {
    const row = raw[r];
    const rowDisplay = display[r];
    const title = getRoadmapTitleFromRow_(cfg, rowDisplay, row);
    if (!title) continue;

    const rowNumber = r + 1;
    const key = fromUpdate
      ? makeRoadmapUpdateGroupKey_(cfg, rowDisplay, row)
      : makeRoadmapBaseRowKey_(cfg, rowNumber, rowDisplay, row);
    const compareKey = makeRoadmapCompareKey_(cfg, rowDisplay, row, title);
    if (!key || !compareKey) continue;

    if (!map[key]) {
      map[key] = {
        source: cfg.source,
        sourceLabel: cfg.sourceLabel,
        year: cfg.year,
        sheetName: sheet.getName(),
        key: key,
        compareKey: compareKey,
        title: title,
        streetName: cfg.source === 'KBU' ? String(rowDisplay[cfg.streetIndex] || row[cfg.streetIndex] || '').trim() : '',
        objectName: cfg.source === 'TR' ? String(rowDisplay[cfg.objectIndex] || row[cfg.objectIndex] || '').trim() : '',
        idOdx: String(rowDisplay[cfg.idIndex] || row[cfg.idIndex] || '').trim(),
        objects: [],
        rowNumbers: [],
        rows: [],
        area: 0,
        cost: 0,
        fromUpdate: !!fromUpdate
      };
    }

    const g = map[key];
    g.rowNumbers.push(rowNumber);
    g.rows.push(row.slice(0, cfg.fixedCols));
    const objectName = String(rowDisplay[cfg.objectIndex] || row[cfg.objectIndex] || '').trim();
    if (objectName && g.objects.indexOf(objectName) === -1) g.objects.push(objectName);
    const id = String(rowDisplay[cfg.idIndex] || row[cfg.idIndex] || '').trim();
    if (id && String(g.idOdx || '').indexOf(id) === -1) g.idOdx = g.idOdx ? (g.idOdx + ', ' + id) : id;
    g.area += toRoadmapNumber_(row[cfg.areaIndex]);
    g.cost += toRoadmapNumber_(row[cfg.costIndex]);
  }

  return Object.keys(map).map(k => {
    const g = map[k];
    g.area = roundRoadmapNumber_(g.area);
    g.cost = roundRoadmapNumber_(g.cost);
    if (!g.objects.length && g.title) g.objects.push(g.title);
    // Для агрегированного ТекРем после группировки по ID сопоставление выполняем по названию объекта.
    // Если под одним ID оказалось несколько названий, берем первое как основное название карточки.
    if (cfg.source === 'TR' && g.objects.length) {
      g.title = g.objects[0];
      g.objectName = g.objects[0];
      g.compareKey = cfg.source + '|object:' + normalizeWeb_(g.objects[0]);
    }
    return g;
  });
}

function getRoadmapTitleFromRow_(cfg, displayRow, rawRow) {
  if (cfg.source === 'KBU') return String(displayRow[cfg.streetIndex] || rawRow[cfg.streetIndex] || '').trim();
  const objectName = String(displayRow[cfg.objectIndex] || rawRow[cfg.objectIndex] || '').trim();
  const id = String(displayRow[cfg.idIndex] || rawRow[cfg.idIndex] || '').trim();
  return objectName || id;
}

function makeRoadmapKey_(cfg, displayRow, rawRow) {
  if (cfg.source === 'KBU') {
    return cfg.source + '|street:' + normalizeWeb_(displayRow[cfg.streetIndex] || rawRow[cfg.streetIndex]);
  }
  const id = normalizeRoadmapOdxId_(displayRow[cfg.idIndex] || rawRow[cfg.idIndex]);
  const objectName = normalizeWeb_(displayRow[cfg.objectIndex] || rawRow[cfg.objectIndex]);
  return cfg.source + '|' + (id ? ('id:' + id) : ('object:' + objectName));
}

function makeRoadmapBaseRowKey_(cfg, rowNumber, displayRow, rawRow) {
  // Текущие листы ДК уже содержат готовые позиции. Поэтому каждую строку
  // держим отдельной позицией, а сопоставление делаем отдельным compareKey.
  return cfg.source + '|row:' + rowNumber + ':' + normalizeWeb_(getRoadmapTitleFromRow_(cfg, displayRow, rawRow));
}

function makeRoadmapUpdateGroupKey_(cfg, displayRow, rawRow) {
  if (cfg.source === 'KBU') {
    return cfg.source + '|street:' + normalizeWeb_(displayRow[cfg.streetIndex] || rawRow[cfg.streetIndex]);
  }
  const id = normalizeRoadmapOdxId_(displayRow[cfg.idIndex] || rawRow[cfg.idIndex]);
  const objectName = normalizeWeb_(displayRow[cfg.objectIndex] || rawRow[cfg.objectIndex]);
  // В листе обновления ТекРем сначала агрегируем именно по ID ODX.
  return cfg.source + '|' + (id ? ('id:' + id) : ('object:' + objectName));
}

function makeRoadmapCompareKey_(cfg, displayRow, rawRow, title) {
  if (cfg.source === 'KBU') {
    return cfg.source + '|street:' + normalizeWeb_(displayRow[cfg.streetIndex] || rawRow[cfg.streetIndex] || title);
  }
  // Сопоставление ТекРем с текущей ДК выполняется по наименованию объекта,
  // так как в текущем листе ID ODX часто отсутствует.
  return cfg.source + '|object:' + normalizeWeb_(displayRow[cfg.objectIndex] || rawRow[cfg.objectIndex] || title);
}

function normalizeRoadmapOdxId_(value) {
  const text = String(value || '').trim();
  if (!text) return '';
  const normalized = normalizeWeb_(text);
  const serviceValues = {'#н/д':true,'#n/a':true,'н/д':true,'n/a':true,'нет':true,'-':true,'—':true};
  if (serviceValues[normalized]) return '';
  return normalized.replace(/\.0+$/, '').replace(/[^a-zа-я0-9]+/gi, '').trim();
}

function compareRoadmapGroups_(base, upd) {
  const changes = [];

  // Для ДК не считаем изменением техническую разницу в хвосте дробной части.
  // Пример: 165352992,3 и 165352992,33 должны считаться одинаковой стоимостью,
  // иначе позиции ошибочно попадают в «Требуется актуализация».
  const areaPrecision = getRoadmapComparePrecision_('area');
  const costPrecision = getRoadmapComparePrecision_('cost');

  const oldArea = roundRoadmapNumberByPrecision_(base.area, areaPrecision);
  const newArea = roundRoadmapNumberByPrecision_(upd.area, areaPrecision);
  if (!isRoadmapNumberEqual_(oldArea, newArea, areaPrecision)) {
    changes.push({field:'area', label:'Площадь благоустройства', oldValue:formatRoadmapNumber_(oldArea), newValue:formatRoadmapNumber_(newArea)});
  }

  const oldCost = roundRoadmapNumberByPrecision_(base.cost, costPrecision);
  const newCost = roundRoadmapNumberByPrecision_(upd.cost, costPrecision);
  if (!isRoadmapNumberEqual_(oldCost, newCost, costPrecision)) {
    changes.push({field:'cost', label:'Стоимость работ', oldValue:formatRoadmapNumber_(oldCost), newValue:formatRoadmapNumber_(newCost)});
  }
  // Состав объектов в КБУ показываем в карточке справочно, но не считаем изменением:
  // основной лист ДК уже содержит готовые позиции дорожной карты и может хранить
  // укрупненную строку по улице без полного состава объектов. Иначе система будет
  // ошибочно подсвечивать улицу как требующую актуализации только из-за детализации
  // листа обновления.
  return changes;
}

function getRoadmapStateCounts_(items) {
  const counts = {total: items.length, ok:0, actualize:0, exclude:0, create:0, needWork:0};
  items.forEach(item => {
    const state = item.cardState || 'ok';
    counts[state] = (counts[state] || 0) + 1;
    if (['actualize','exclude','create'].indexOf(state) !== -1) counts.needWork++;
  });
  return counts;
}

function applyRoadmapAction(payload) {
  const user = requireAdmin_();
  payload = payload || {};
  const cfg = getRoadmapConfigBySource_(payload.source, payload.year);
  const action = String(payload.action || '').trim();
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  const baseSheet = ss.getSheetByName(cfg.baseSheet);
  const updateSheet = ss.getSheetByName(cfg.updateSheet);
  if (!baseSheet) throw new Error('Лист "' + cfg.baseSheet + '" не найден.');
  if (!updateSheet && action !== 'exclude') throw new Error('Лист "' + cfg.updateSheet + '" не найден.');

  const baseGroups = readRoadmapGroups_(baseSheet, cfg, false);
  const updateGroups = updateSheet ? readRoadmapGroups_(updateSheet, cfg, true) : [];
  const baseGroup = baseGroups.find(g => g.key === payload.key);
  const updateKey = String(payload.updateKey || payload.key || '');
  const updateGroup = updateGroups.find(g => g.key === updateKey);

  if (action === 'exclude') {
    if (!baseGroup) throw new Error('Позиция для исключения не найдена в текущей дорожной карте.');
    deleteRowsDescending_(baseSheet, baseGroup.rowNumbers);
    logRoadmapAction_(user, cfg.sourceLabel, 'Исключить из дорожной карты', baseGroup.title, '', '');
    logPlatformChange_('roadmap', 'action', cfg.source + ':' + baseGroup.key, {year:cfg.year, source:cfg.source, key:baseGroup.key, action:action, title:baseGroup.title});
    return {success:true, message:'Позиция исключена из текущей дорожной карты.'};
  }

  if (action === 'actualize') {
    if (!baseGroup) throw new Error('Позиция для актуализации не найдена в текущей дорожной карте.');
    if (!updateGroup) throw new Error('Позиция не найдена на листе обновления.');
    deleteRowsDescending_(baseSheet, baseGroup.rowNumbers);
    appendRoadmapGroup_(baseSheet, cfg, updateGroup);
    logRoadmapAction_(user, cfg.sourceLabel, 'Актуализировать позицию', updateGroup.title, '', '');
    logPlatformChange_('roadmap', 'action', cfg.source + ':' + updateGroup.key, {year:cfg.year, source:cfg.source, key:updateGroup.key, action:action, title:updateGroup.title});
    return {success:true, message:'Позиция актуализирована по листу обновления.'};
  }

  if (action === 'create') {
    if (!updateGroup) throw new Error('Новая позиция не найдена на листе обновления.');
    appendRoadmapGroup_(baseSheet, cfg, updateGroup);
    logRoadmapAction_(user, cfg.sourceLabel, 'Добавить в дорожную карту', updateGroup.title, '', '');
    logPlatformChange_('roadmap', 'action', cfg.source + ':' + updateGroup.key, {year:cfg.year, source:cfg.source, key:updateGroup.key, action:action, title:updateGroup.title});
    return {success:true, message:'Позиция добавлена в текущую дорожную карту.'};
  }

  throw new Error('Неизвестное действие с дорожной картой.');
}

function appendRoadmapGroup_(sheet, cfg, group) {
  const row = buildRoadmapOutputRow_(cfg, group);
  sheet.getRange(sheet.getLastRow() + 1, 1, 1, row.length).setValues([row]);
}

function buildRoadmapOutputRow_(cfg, group) {
  if (cfg.source === 'KBU') {
    return [group.idOdx || '', group.streetName || group.title || '', (group.objects || []).join('; '), roundRoadmapNumberByPrecision_(group.area, 2), roundRoadmapNumberByPrecision_(group.cost, 2)];
  }
  return [(group.objects || [group.objectName || group.title || '']).join('; '), group.idOdx || '', roundRoadmapNumberByPrecision_(group.area, 2), roundRoadmapNumberByPrecision_(group.cost, 2)];
}

function getRoadmapConfigBySource_(source, year) {
  const cfgs = getRoadmapYearConfigs_(year);
  source = String(source || '').toUpperCase();
  if (source === 'KBU') return cfgs.kbu;
  if (source === 'TR') return cfgs.tr;
  throw new Error('Неизвестный источник дорожной карты: ' + source);
}

function toRoadmapNumber_(value) {
  if (typeof value === 'number') return isFinite(value) ? value : 0;
  const text = String(value || '').replace(/\s/g, '').replace(',', '.').replace(/[^0-9.\-]/g, '');
  const n = Number(text);
  return isFinite(n) ? n : 0;
}

function roundRoadmapNumber_(n) {
  return roundRoadmapNumberByPrecision_(n, 6);
}

function roundRoadmapNumberByPrecision_(n, precision) {
  const p = Math.pow(10, Number(precision) || 0);
  return Math.round((Number(n) || 0) * p) / p;
}

function getRoadmapComparePrecision_(field) {
  // Стоимость в дорожных картах часто приходит из разных источников с разной
  // разрядностью: 165352992,3 и 165352992,33. Для контроля ДК это не должно
  // создавать ложное изменение, поэтому стоимость сравниваем до 1 знака.
  if (String(field || '').toLowerCase() === 'cost') return 1;
  // Площадь оставляем до 2 знаков, чтобы не терять реальные изменения площади.
  return 2;
}

function isRoadmapNumberEqual_(a, b, precision) {
  const p = Math.pow(10, Number(precision) || 0);
  return Math.abs((Number(a) || 0) - (Number(b) || 0)) < (0.5 / p);
}

function formatRoadmapNumber_(n) {
  const value = roundRoadmapNumberByPrecision_(n, 2);
  return String(value).replace('.', ',');
}

function logRoadmapAction_(user, source, action, objectName, oldValue, newValue) {
  try {
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    let sheet = ss.getSheetByName('История_действий');
    if (!sheet) sheet = ss.insertSheet('История_действий');
    if (sheet.getLastRow() === 0) sheet.appendRow(['Дата и время','Email','ФИО','Роль','Раздел','Действие','Объект','Старое значение','Новое значение']);
    sheet.appendRow([new Date(), user.email, user.fullName, user.role, 'Формирование дорожной карты / ' + source, action, objectName, oldValue, newValue]);
  } catch (e) {}
}
