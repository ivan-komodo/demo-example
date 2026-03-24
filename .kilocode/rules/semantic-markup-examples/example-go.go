//go:build ignore

// Эталонные фрагменты семантической разметки для Go (справочник).

package semanticmarkup

// --- Контракт + чанк (линейные комментарии) ---
// [START_PARSE_CONFIG]
// ANCHOR: Загрузка конфигурации агента
// @PreConditions:
// - path указывает на существующий файл
// @PostConditions:
// - при ошибке — обёрнутая ошибка с контекстом
// PURPOSE: Разбор JSON-конфига с валидацией обязательных полей.
func ParseConfig(path string) error {
	_ = path
	return nil
}

// [END_PARSE_CONFIG]

// === CHUNK: STORAGE_ADAPTER_V1 [PERSISTENCE] ===
// Описание: Адаптер к хранилищу Chrome (обёртка для тестов).
// Dependencies: none (интерфейсы на уровне вызова)
type StorageAdapter struct{}

// === END_CHUNK: STORAGE_ADAPTER_V1 ===

/*
   LIFECYCLE_ANCHOR: WorkerStates (в блочном комментарии — удобно для многострочных списков)
   STATES:
     Idle -> Running [trigger: Start()]
     Running -> Stopping [trigger: Stop()]
     Stopping -> Idle [trigger: ack()]
   END_LIFECYCLE_ANCHOR
*/

type WorkerPhase int
