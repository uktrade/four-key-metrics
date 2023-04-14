from display import DisplayShell

task_runner = DisplayShell()

# Remove old csvs
task_runner.do_remove_reports('csv')

# Run 4-key-metrics script
task_runner.do_four_key_metrics('csv')
