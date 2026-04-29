import "dotenv/config";

import chalk from "chalk";

const checks = [
  ["NEXT_PUBLIC_API_URL", process.env.NEXT_PUBLIC_API_URL],
  ["DATABASE_URL", process.env.DATABASE_URL],
  ["NODE_ENV", process.env.NODE_ENV]
];

console.log(chalk.cyan("Colsabor frontend doctor"));

for (const [name, value] of checks) {
  const status = value ? chalk.green("configurado") : chalk.yellow("pendiente");
  console.log(`${chalk.bold(name)}: ${status}`);
}

if (!process.env.DATABASE_URL) {
  console.log(chalk.gray("Prisma queda listo, pero no se generan migraciones sin DATABASE_URL."));
}
