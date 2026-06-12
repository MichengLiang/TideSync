import { describe, expect, test } from "vitest";
import { runCli } from "./cli.js";

describe("TideSync CLI", () => {
	test("prints a hello message by default", async () => {
		await expect(runCli([])).resolves.toEqual({
			exitCode: 0,
			stderr: "",
			stdout: "Hello from TideSync.\n",
		});
	});

	test("prints a hello message for a named recipient", async () => {
		await expect(runCli(["--name", "Ada"])).resolves.toEqual({
			exitCode: 0,
			stderr: "",
			stdout: "Hello, Ada, from TideSync.\n",
		});
	});

	test("prints the package version", async () => {
		await expect(runCli(["--version"])).resolves.toEqual({
			exitCode: 0,
			stderr: "",
			stdout: "0.0.0\n",
		});
	});

	test("prints Commander help", async () => {
		const result = await runCli(["--help"]);

		expect(result.exitCode).toBe(0);
		expect(result.stderr).toBe("");
		expect(result.stdout).toContain("Usage: tidesync [options]");
		expect(result.stdout).toContain("--name <name>");
	});
});
