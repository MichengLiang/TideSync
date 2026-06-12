import { Command, CommanderError } from "commander";

export type CliRunResult = {
	exitCode: number;
	stdout: string;
	stderr: string;
};

type CliOptions = {
	name?: string;
};

const version = "0.0.0";

function helloMessage(name?: string) {
	return name ? `Hello, ${name}, from TideSync.\n` : "Hello from TideSync.\n";
}

export async function runCli(args: string[]): Promise<CliRunResult> {
	let stdout = "";
	let stderr = "";
	const program = new Command();

	program
		.name("tidesync")
		.description("TideSync command line interface.")
		.version(version)
		.option("--name <name>", "name to greet")
		.exitOverride()
		.configureOutput({
			writeOut: (value) => {
				stdout += value;
			},
			writeErr: (value) => {
				stderr += value;
			},
		})
		.action((options: CliOptions) => {
			stdout += helloMessage(options.name);
		});

	try {
		await program.parseAsync(args, { from: "user" });
		return { exitCode: 0, stdout, stderr };
	} catch (error) {
		if (error instanceof CommanderError) {
			return {
				exitCode: error.exitCode,
				stdout,
				stderr,
			};
		}

		return {
			exitCode: 1,
			stdout,
			stderr:
				error instanceof Error ? `${error.message}\n` : `${String(error)}\n`,
		};
	}
}
