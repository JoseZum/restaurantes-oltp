import { Sequelize } from "sequelize";
import mongoose from "mongoose";
import dotenv from "dotenv";
dotenv.config();

let sequelize;
let mongoConn = null;

if (process.env.NODE_ENV === "test") {
  // Testing con SQLite en memoria
  sequelize = new Sequelize({
    dialect: "sqlite",
    storage: ":memory:",
    logging: false,
  });
} else if (process.env.DB_ENGINE === "postgres") {
  // PostgreSQL en dev/prod
  sequelize = new Sequelize({
    dialect: "postgres",
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    username: process.env.DB_USER,
    password: process.env.DB_PASS,
    database: process.env.DB_NAME,
    logging: false,
  });
} else if (process.env.DB_ENGINE === "mongo") {
  // MongoDB conexion con mongoose
  mongoConn = mongoose.connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("Conectado a MongoDB"))
  .catch((err) => console.error("Error al conectar a MongoDB:", err));
}

export const initDB = () => sequelize?.authenticate?.();
export { sequelize, mongoConn };
