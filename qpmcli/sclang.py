from cement.core import controller
import os.path
import qpmlib.sclang_process as process
import qpmlib.sclang_testing as testing

class SCLang_Base(controller.CementBaseController):
	class Meta:
		label = 'sc'
		stacked_on = 'base'
		stacked_type = 'nested'
		description = 'do things with sclang'

class SCLang_AbstractBase(controller.CementBaseController):
	class Meta:
		stacked_on = 'sc'
		stacked_type = 'nested'
		base_arguments = [
            (['-p', '--path'], dict(default=os.getcwd(), help='Path to supercollider installation or config.yaml')),
            (['-i', '--include'], dict(nargs='*', help='Path to include in ClassLib')),
		]

	def _collect(self):
		(arguments, commands) = super(SCLang_AbstractBase, self)._collect()
		return (arguments + self._meta.base_arguments, commands)

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
		sclang = process.find_sclang_executable(self.app.pargs.path)
		code = self.app.pargs.code[0]

		output, error = process.do_execute(sclang, code)

		if output:
			self.app.render({ "result": output })
		else:
			self.app.render({ "error": error })


class SCLang_ListTests(SCLang_AbstractBase):
	class Meta:
		label = 'listtests'
		description = 'List unit tests available in sclang.'

	@controller.expose(help="List unit tests available in sclang.")
	def default(self):
		sclang = process.find_sclang_executable(self.app.pargs.path)
		try:
			result = testing.find_tests(sclang)
			self.app.render({ "result": result })
		except Exception, e:
			self.app.render({ "error": e })

class SCLang_RunTest(SCLang_AbstractBase):
	class Meta:
		label = 'test'
		description = 'Run a test.'
		arguments = [
			(['-o', '--print-output'], {
				'help': 'print output of unit tests'
			}),
			(['test'], {
				'help': 'test to run',
				'action': 'store',
				'nargs': '*'
			})
		]

	@controller.expose(help="Run a unit test. Specify one or multiple using the form 'Class:test', or 'Class:*' for all tests.")
	def default(self):
		sclang = process.find_sclang_executable(self.app.pargs.path)

		if sclang:
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

			try:
				test_run = testing.SCTestRun(sclang, test_plan, includes=self.app.pargs.include)
				test_run.print_stdout = self.app.pargs.print_output
				result = test_run.run()
				summary = generate_summary(result, test_run.duration)

				for test in result['tests']:
					self.app.render({ 'test_result': test })
				self.app.render({ 'test_summary': summary })

				if summary['failed_tests'] > 0:
					self.app.close(1)

			except Exception, e:
				self.app.render({ "error": e })

def generate_summary(test_plan, duration):
	total = 0
	failed = 0
	for test in test_plan.get('tests', []):
		if not(test.get('results')):
			if not(test.get('error')):
				test['results'] = [{'test': 'completed without error', 'pass': 'true'}]
			else:
				test['results'] = [{'test': 'completed without error', 'pass': 'false'}]

		for subtest in test.get('results', []):
			total += 1
			if not(subtest.get('pass')) or subtest.get('pass') == 'false':
				failed += 1

	return {
		'total_tests': total,
		'failed_tests': failed,
		'duration': duration
	}







