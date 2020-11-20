from cement.core import controller
import os.path
import qpm.sclang_process as process
import qpm.sclang_testing as testing

from .base import *

class SCLang_Execute(SCLang_AbstractBase):
	class Meta:
		label = 'execute'
		description = 'Execute a command in sclang'
		arguments = [
			(['--timeout', '-t'], {
				'help': 'Execution timeout.',
				'action': 'store'
			}),
			(['code'], {
				'help': 'sclang code to interpret',
				'action': 'store',
				'nargs': '*'
			})
		]

	@controller.expose(help="Execute some code in sclang.", hide=True)
	def default(self):
		if os.environ.get('QPM_DEBUG') != '0':
			self.app.pargs.print_output = True

		sclang = process.find_sclang_executable(self.app.pargs.path)
		code = self.app.pargs.code[0]

		output, error = process.do_execute(
			sclang,
			code,
			self.app.pargs.include,
			self.app.pargs.exclude,
			self.app.pargs.print_output
		)

		if output:
			self.app.render({ "result": output })
		else:
			self.app.render(error, 'error')


class SCLang_ListTests(SCLang_AbstractBase):
	class Meta:
		label = 'test.list'
		description = 'List unit tests available in sclang.'

	@controller.expose(help="List unit tests available in sclang.")
	def default(self):
		if os.environ.get('QPM_DEBUG') != '0':
			self.app.pargs.print_output = True

		sclang = process.find_sclang_executable(self.app.pargs.path)
		try:
			result = testing.find_tests(sclang, self.app.pargs.print_output,
				self.app.pargs.include, self.app.pargs.exclude)
			self.app.render(result, 'test_list')
		except Exception as e:
			self.app.render(e, 'error')

class SCLang_RunTest(SCLang_AbstractBase):
	class Meta:
		label = 'test.run'
		description = 'Run a test.'
		arguments = [
			(['test'], {
				'help': 'test to run',
				'action': 'store',
				'nargs': '*'
			}),
			(['-l', '--location'], {
				'help': 'Location of test plan file. If no tests are specified, the test plan will be resumed.',
				'action': 'store',
				'nargs': '?'
			})
		]

	@controller.expose(help="Run a unit test. Specify one or multiple using the form 'Class:test', or 'Class:*' for all tests.")
	def default(self):
		if os.environ.get('QPM_DEBUG') != '0':
			self.app.pargs.print_output = True

		sclang = process.find_sclang_executable(self.app.pargs.path)

		if sclang:
			test_plan = None
			test_plan_path = None

			if self.app.pargs.test:
				test_plan = {
					'tests': []
				}

				for test_specifier in self.app.pargs.test:
					specifiers = test_specifier.split(':')
					test_suite = specifiers[0]
					if len(specifiers) > 1:
						test_name = specifiers[1]
					else:
						test_name = "*"

					test_plan['tests'].append({
						'suite': test_suite, 'test': test_name
					})

			if self.app.pargs.location:
				test_plan_path = self.app.pargs.location

			try:
				test_run = testing.SCTestRun(sclang, test_plan=test_plan, test_plan_path=test_plan_path, includes=self.app.pargs.include, excludes=self.app.pargs.exclude)
				test_run.print_stdout = self.app.pargs.print_output
				result = test_run.run()
				summary = generate_summary(result, test_run.duration)

				for test in result['tests']:
					self.app.render(test, 'test_result')
				self.app.render(summary, 'test_summary')

				if summary['failed_tests'] > 0:
					#self.app.close(summary['failed_tests'])
					self.app.close(summary['failed_tests'])
				else:
					self.app.close(0)

			except Exception as e:
				self.app.render(e, 'error')
				self.app.close(1)

def generate_summary(test_plan, duration):
	total = 0
	failed = 0
	skipped = 0
	for test in test_plan.get('tests', []):
		if not(test.get('results')):
			if test.get('skip'):
				skipped += 1
			else:
				if not(test.get('error')):
					test['results'] = [{'test': 'completed without error', 'pass': 'true'}]
				else:
					test['results'] = [{'test': 'completed without error', 'pass': 'false'}]

		for subtest in test.get('results', []):
			total += 1
			if not(subtest.get('pass')) or subtest.get('pass') == 'false':
				if not(test.get('skip')):
					failed += 1

	return {
		'total_tests': total,
		'failed_tests': failed,
		'skipped_tests': skipped,
		'duration': duration
	}
