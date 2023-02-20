from bot import dp, executor

executor.start_polling(dp, timeout=60, skip_updates=True)
