import csv
import logging
import os
from typing import Dict, Iterator, List, Any
from fastapi import HTTPException, status
import openpyxl

from backend.src.v1.filesystem.infrastructure.excel_dto.dtos import ContractDTO, ContractItemDTO, ObjectDTO, WorkDTO


logger = logging.getLogger(__name__)

# Дефолтный маппинг. Ключ — внутреннее поле системы, значения — синонимы в Excel
FIELD_MAPPING = {
    # Object
    "obj_title": ["Объект", "Наименование объекта", "Название объекта", "Object Title"],
    "obj_address": ["Адрес", "Адрес объекта", "Address"],
    "obj_district": ["Округ", "Административный округ", "Район", "District"],
    # Work
    "work_title": ["Работа", "Наименование работы", "Вид работ", "Work Title"],
    "work_cost": ["Стоимость работы", "Сумма работы", "Work Cost"],
    "work_deadline": ["Срок выполнения", "Срок работы", "Дедлайн", "Work Deadline"],
    # Contract
    "contract_id": ["Договор", "Номер договора", "Contract ID"],
    "contract_date_signed": ["Дата договора", "Дата подписания", "Date Signed"],
    "contract_planned_start": ["Дата начала", "Плановое начало", "Planned Start"],
    "contract_planned_end": ["Дата окончания", "Плановое окончание", "Planned End"],
    # ContractItem
    "item_title": ["Позиция договора", "Наименование позиции", "Item Title"],
    "item_quantity": ["Количество", "Объем", "Quantity"],
    "item_unit": ["Ед. изм.", "Единица измерения", "Unit"],
    "item_price_per_unit": ["Цена за единицу", "Тариф", "Price per Unit"]
}

class ExcelParser:
    def __init__(self, file_path: str, custom_mapping: Dict[str, List[str]] | None = None):
        self.file_path = file_path
        self.mapping = custom_mapping or FIELD_MAPPING
        self.col_indices: Dict[str, int] = {}
        self._ext = os.path.splitext(file_path)[1].lower() # получение расширения файла

    def parse(self) -> List[ObjectDTO]:
        try:
            rows_generator = self._get_rows_generator()

            try:
                headers = next(rows_generator)
                self._map_headers(headers)
            except StopIteration:
                raise ValueError("Файл пуст")
            finally:
                self._validate_required_mappings()

            tree_data: Dict[str, Dict[str, Dict[str, ContractDTO]]] = {}
            objects_meta: Dict[str, Dict[str, Any]] = {}
            works_meta: Dict[str, Dict[str, Any]] = {}

            for row_idx, row in enumerate(rows_generator, start=2):
                if not any(row):
                    continue

                try:
                    # Извлекаем данные, используя индексы колонок
                    obj_title = self._get_val(row, "obj_title")
                    work_title = self._get_val(row, "work_title")

                    if not obj_title or not work_title:
                        continue  # Объект и Работа — обязательный минимум для строки

                    obj_title = str(obj_title).strip()
                    work_title = str(work_title).strip()

                    # Сохраняем метаданные для объектов и работ
                    if obj_title not in objects_meta:
                        objects_meta[obj_title] = {
                            "address": self._get_val(row, "obj_address"),
                            "district": self._get_val(row, "obj_district")
                        }
                    
                    work_key = f"{obj_title}||{work_title}"
                    if work_key not in works_meta:
                        works_meta[work_key] = {
                            "cost": self._get_val(row, "work_cost"),
                            "deadline": self._get_val(row, "work_deadline")
                        }

                    # Начинаем строить дерево
                    if obj_title not in tree_data:
                        tree_data[obj_title] = {}
                    if work_title not in tree_data[obj_title]:
                        tree_data[obj_title][work_title] = {}

                    # Если в строке есть данные договора
                    contract_id = self._get_val(row, "contract_id")
                    if contract_id:
                        contract_id = str(contract_id).strip()
                        
                        if contract_id not in tree_data[obj_title][work_title]:
                            tree_data[obj_title][work_title][contract_id] = ContractDTO(
                                contract_id=contract_id,
                                date_signed=self._get_val(row, "contract_date_signed"),
                                planned_start=self._get_val(row, "contract_planned_start"),
                                planned_end=self._get_val(row, "contract_planned_end")
                            )

                        current_contract = tree_data[obj_title][work_title][contract_id]

                        # Если есть спецификация (ContractItem) в строке
                        item_title = self._get_val(row, "item_title")
                        if item_title:
                            item_dto = ContractItemDTO(
                                title=str(item_title).strip(),
                                quantity=self._get_val(row, "item_quantity"),
                                unit=str(self._get_val(row, "item_unit") or "шт."),
                                price_per_unit=self._get_val(row, "item_price_per_unit")
                            )
                            current_contract.items.append(item_dto)

                except Exception as e:
                    logger.warning(f"Ошибка при обработке строки {row_idx}: {e}")
                    continue

            #wb.close()

            # Превращаем агрегированную структуру обратно в красивый список DTO
            result_objects: List[ObjectDTO] = []
            for obj_name, works_dict in tree_data.items():
                obj_dto = ObjectDTO(
                    title=obj_name,
                    address=objects_meta[obj_name]["address"],
                    district=objects_meta[obj_name]["district"]
                )

                for w_title, contracts_dict in works_dict.items():
                    w_meta = works_meta[f"{obj_name}||{w_title}"]
                    work_dto = WorkDTO(
                        title=w_title,
                        cost=w_meta["cost"],
                        deadline=w_meta["deadline"]
                    )

                    for contract_dto in contracts_dict.values():
                        # Пересчитываем стоимости по позициям спецификации
                        contract_dto.calculate_totals()
                        work_dto.contracts.append(contract_dto)

                    obj_dto.works.append(work_dto)

                result_objects.append(obj_dto)

            return result_objects
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_rows_generator(self) -> Iterator[tuple]:
        """Возвращает генератор строк независимо от формата файла."""
        if self._ext == ".csv":
            return self._read_csv()
        elif self._ext in (".xlsx", ".xlsm", ".xltx", ".xltm"):
            return self._read_xlsx()
        elif self._ext == ".xls":
            return self._read_xls()
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {self._ext}")

    def _read_xlsx(self) -> Iterator[tuple]:
        wb = openpyxl.load_workbook(self.file_path, read_only=True, data_only=True)
        sheet = wb.active
        if sheet is None:
            logger.error("Excel sheet not found (= None)")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        yield from sheet.iter_rows(values_only=True)
        wb.close()

    def _read_xls(self) -> Iterator[tuple]:
        import xlrd  # pip install xlrd
        wb = xlrd.open_workbook(self.file_path)
        sheet = wb.sheet_by_index(0)
        for row_idx in range(sheet.nrows):
            yield tuple(sheet.row_values(row_idx))

    def _read_csv(self) -> Iterator[tuple]:
        # определяем разделитель и кодировку автоматически
        encoding = self._detect_encoding()
        with open(self.file_path, "r", encoding=encoding, newline="") as f:
            sample = f.read(4096)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            except csv.Error:
                dialect = csv.excel  # запятая по умолчанию
            reader = csv.reader(f, dialect)
            for row in reader:
                yield tuple(row)

    def _detect_encoding(self) -> str:
        """Простая эвристика: UTF-8 (с BOM или без), иначе cp1251."""
        with open(self.file_path, "rb") as f:
            raw = f.read(4)
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                f.read()
            return "utf-8"
        except UnicodeDecodeError:
            return "cp1251"

    def _get_val(self, row: tuple, field_key: str) -> Any:
        idx = self.col_indices.get(field_key)
        return row[idx] if idx is not None and idx < len(row) else None

    def _map_headers(self, headers: tuple):
        for field, aliases in self.mapping.items():
            for idx, cell_value in enumerate(headers):
                if cell_value is None:
                    continue
                cell_str = str(cell_value).strip().lower()
                if cell_str in [alias.lower() for alias in aliases]:
                    self.col_indices[field] = idx
                    break

    def _validate_required_mappings(self):
        # Базовые обязательные поля для успешного импорта
        required = {"obj_title", "work_title"}
        missing = required - set(self.col_indices.keys())
        if missing:
            raise ValueError(f"Не найдены обязательные колонки: {', '.join(missing)}")