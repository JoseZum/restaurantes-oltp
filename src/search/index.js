import express from 'express';
import dotenv   from 'dotenv';
import searchRoutes from './search.routes.js';
import { ensureProductsIndex } from './bootstrap.js';

dotenv.config();

await ensureProductsIndex();

const app = express();
app.use(express.json());
app.use('/search', searchRoutes);

const PORT = process.env.SEARCH_PORT || 4000;
app.listen(PORT, () => {
  console.log(`Microservicio de busqueda activo en http://localhost:${PORT}`);
});
