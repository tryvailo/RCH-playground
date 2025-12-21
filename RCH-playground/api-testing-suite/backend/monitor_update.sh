#!/bin/bash
# Скрипт для мониторинга обновления CQC базы данных

LOG_FILE="/tmp/cqc_full_update.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Лог файл не найден: $LOG_FILE"
    exit 1
fi

echo "=" | awk '{printf "%.80s\n", $0"="}'
echo "🚀 МОНИТОРИНГ ОБНОВЛЕНИЯ CQC БАЗЫ ДАННЫХ"
echo "=" | awk '{printf "%.80s\n", $0"="}'

# Get current batch
CURRENT_BATCH=$(grep -o "Batch [0-9]*/[0-9]*" "$LOG_FILE" | tail -1 | grep -o "[0-9]*" | head -1)
TOTAL_BATCHES=$(grep -o "Batch [0-9]*/[0-9]*" "$LOG_FILE" | tail -1 | grep -o "[0-9]*" | tail -1)

if [ -z "$CURRENT_BATCH" ] || [ -z "$TOTAL_BATCHES" ]; then
    echo "⏳ Процесс еще не начал обрабатывать батчи..."
    echo "Последние строки лога:"
    tail -5 "$LOG_FILE"
    exit 0
fi

# Calculate progress
PROGRESS=$(echo "scale=1; $CURRENT_BATCH * 100 / $TOTAL_BATCHES" | bc)
REMAINING=$((TOTAL_BATCHES - CURRENT_BATCH))
ESTIMATED_MIN=$(echo "scale=1; $REMAINING / 60" | bc)

# Count updates
UPDATED_COUNT=$(grep -c "✅.*Updated" "$LOG_FILE" 2>/dev/null || echo "0")

echo ""
echo "📊 Текущий статус:"
echo "   Batch: $CURRENT_BATCH/$TOTAL_BATCHES ($PROGRESS%)"
echo "   Обновлено домов: $UPDATED_COUNT"
echo ""
echo "⏱️  Оценка времени:"
echo "   Осталось батчей: $REMAINING"
echo "   Ожидаемое время: ~$ESTIMATED_MIN минут"
echo ""
echo "📈 Последние обновления:"
tail -10 "$LOG_FILE" | grep "✅.*Updated" | tail -5
echo ""
echo "=" | awk '{printf "%.80s\n", $0"="}'
echo "💡 Для мониторинга в реальном времени:"
echo "   tail -f $LOG_FILE"
echo "=" | awk '{printf "%.80s\n", $0"="}'

