# Documentación API - Finanzas Backend

Guía completa de la API REST para el desarrollo del frontend.

**Base URL:** `http://127.0.0.1:8000/api/`

---

## Tabla de contenido

- [Autenticación](#autenticación)
  - [Flujo de activación](#flujo-de-activación)
  - [Cómo usar el JWT](#cómo-usar-el-jwt)
  - [Refresh token](#refresh-token)
- [Endpoints](#endpoints)
  - [POST /api/activate-key/](#post-apiactivate-key)
  - [POST /api/expenses/](#post-apiexpenses)
  - [GET /api/expenses/](#get-apiexpenses)
  - [GET /api/expenses/{id}/](#get-apiexpensesid)
  - [PUT /api/expenses/{id}/](#put-apiexpensesid)
  - [POST /api/savings/goals/](#post-apisavingsgoals)
  - [GET /api/savings/goals/](#get-apisavingsgoals)
  - [GET /api/savings/goals/{id}/](#get-apisavings-goalsid)
  - [PUT /api/savings/goals/{id}/](#put-apisavings-goalsid)
  - [DELETE /api/savings/goals/{id}/](#delete-apisavings-goalsid)
  - [POST /api/savings/goals/{id}/deposit/](#post-apisavings-goalsiddeposit)
  - [POST /api/savings/goals/{id}/withdraw/](#post-apisavings-goalsidwithdraw)
  - [GET /api/savings/goals/{id}/movements/](#get-apisavings-goalsidmovements)
  - [POST /api/savings/goals/{id}/participants/](#post-apisavings-goalsidparticipants)
- [Códigos de error](#códigos-de-error)
- [Estructuras de datos](#estructuras-de-datos)

---

## Autenticación

### Flujo de activación

```
1. Frontend envía POST /api/activate-key/ con { key, name }
2. Backend valida la llave
3. Si es válida → crea el usuario + retorna JWT
4. Si no es válida → retorna error 400
```

**Después de activar, el usuario NUNCA necesita hacer login de nuevo** — el JWT se renueva con el refresh token.

### Cómo usar el JWT

Incluir el token en cada petición autenticada:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

En JavaScript/Fetch:
```javascript
fetch('http://127.0.0.1:8000/api/expenses/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

En React Native con Axios:
```javascript
api.get('/api/expenses/', {
  headers: {
    Authorization: `Bearer ${accessToken}`
  }
})
```

### Refresh token

- **Access token**: 60 min de vida (configurable)
- **Refresh token**: 7 días de vida

Cuando el access token expira, usar el refresh token para obtener uno nuevo. (Endpoint de refresh no implementado aún, se agregará en un paso futuro).

---

## Endpoints

---

### POST `/api/activate-key/`

Activa una llave de acceso, crea la cuenta de usuario y retorna JWT.

**No requiere autenticación.**

#### Request

```json
{
  "key": "FINANZAS-2026-USUARIO-1",
  "name": "Juan"
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `key` | string | Sí | Llave de activación |
| `name` | string | Sí | Nombre del usuario |

#### Response — 201 Created

```json
{
  "detail": "Cuenta activada exitosamente.",
  "user": {
    "id": 1,
    "name": "Juan"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "refresh": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

#### Errores

| Código | Body | Causa |
|---|---|---|
| 400 | `{"detail": "La llave ingresada no es válida."}` | La llave no existe en la BD |
| 400 | `{"detail": "La llave ya fue utilizada anteriormente."}` | La llave ya fue activada |
| 400 | `{"key": ["Este campo es requerido."]}` | Falta el campo `key` |
| 400 | `{"name": ["Este campo es requerido."]}` | Falta el campo `name` |

---

### POST `/api/expenses/`

Crea un nuevo gasto. El `usuario` se obtiene automáticamente del JWT.

**Requiere autenticación.**

#### Request

```json
{
  "categoria": "Alimentación",
  "fecha": "2026-07-15",
  "descripcion": "Almuerzo en resturante",
  "valor": 45000,
  "compartido": false
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `categoria` | string | Sí | Categoría del gasto (máx 100 caracteres) |
| `fecha` | string (date) | Sí | Fecha del gasto. Formato: `YYYY-MM-DD` |
| `descripcion` | string | Sí | Descripción (máx 255 caracteres) |
| `valor` | number | Sí | Valor monetario (hasta 12 dígitos, 2 decimales) |
| `compartido` | boolean | No | Default: `false` |

#### Response — 201 Created

```json
{
  "id": 1,
  "usuario_nombre": "Juan",
  "categoria": "Alimentación",
  "fecha": "2026-07-15",
  "descripcion": "Almuerzo en resturante",
  "valor": "45000.00",
  "compartido": false,
  "created_at": "2026-07-15T12:00:00-05:00"
}
```

#### Errores

| Código | Causa |
|---|---|
| 401 | No autenticado / token inválido |
| 400 | Campos faltantes o inválidos |

---

### GET `/api/expenses/`

Lista los gastos del usuario autenticado. Incluye:
- Todos los gastos propios
- Gastos de otros usuarios donde `compartido = true`

**Requiere autenticación.**

#### Response — 200 OK

```json
[
  {
    "id": 1,
    "usuario_nombre": "Juan",
    "categoria": "Alimentación",
    "fecha": "2026-07-15",
    "descripcion": "Almuerzo en resturante",
    "valor": "45000.00",
    "compartido": false,
    "created_at": "2026-07-15T12:00:00-05:00"
  },
  {
    "id": 2,
    "usuario_nombre": "María",
    "categoria": "Transporte",
    "fecha": "2026-07-14",
    "descripcion": "Uber al trabajo",
    "valor": "12000.00",
    "compartido": true,
    "created_at": "2026-07-14T08:30:00-05:00"
  }
]
```

> **Nota**: Los gastos compartidos muestran el `usuario_nombre` del dueño original.

---

### GET `/api/expenses/{id}/`

Obtiene el detalle de un gasto específico.

- Si es tu gasto → lo ves
- Si es gasto de otro usuario y es compartido → lo ves
- Si es gasto de otro usuario y NO es compartido → 404

**Requiere autenticación.**

#### Response — 200 OK

```json
{
  "id": 1,
  "usuario_nombre": "Juan",
  "categoria": "Alimentación",
  "fecha": "2026-07-15",
  "descripcion": "Almuerzo en resturante",
  "valor": "45000.00",
  "compartido": false,
  "created_at": "2026-07-15T12:00:00-05:00"
}
```

#### Errores

| Código | Causa |
|---|---|
| 404 | El gasto no existe o no tienes acceso |
| 401 | No autenticado |

---

### PUT `/api/expenses/{id}/`

Actualiza un gasto. Solo el propietario puede actualizar. Se puede enviar solo los campos que se quieren modificar (partial update).

**Requiere autenticación.**

#### Request (parcial)

```json
{
  "valor": 50000,
  "compartido": true
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `categoria` | string | No | Categoría |
| `fecha` | string (date) | No | Fecha `YYYY-MM-DD` |
| `descripcion` | string | No | Descripción |
| `valor` | number | No | Valor monetario |
| `compartido` | boolean | No | Visibilidad |

#### Response — 200 OK

```json
{
  "id": 1,
  "usuario_nombre": "Juan",
  "categoria": "Alimentación",
  "fecha": "2026-07-15",
  "descripcion": "Almuerzo en resturante",
  "valor": "50000.00",
  "compartido": true,
  "created_at": "2026-07-15T12:00:00-05:00"
}
```

#### Errores

| Código | Causa |
|---|---|
| 403 | Intentas editar un gasto de otro usuario |
| 404 | El gasto no existe o no es tuyo |
| 401 | No autenticado |

---

### POST `/api/savings/goals/`

Crea una meta de ahorro. El usuario autenticado es el propietario.

**Requiere autenticación.**

#### Request

```json
{
  "name": "Viaje a Japón",
  "description": "Ahorro para el viaje de diciembre",
  "target_amount": 5000000,
  "currency": "COP",
  "deadline": "2026-12-01",
  "is_shared": false
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `name` | string | Sí | Nombre de la meta (máx 255) |
| `description` | string | No | Descripción (default: "") |
| `target_amount` | number | Sí | Monto objetivo (máx 15 dígitos, 2 decimales, mínimo 0.01) |
| `currency` | string | No | Moneda (default: "COP") |
| `deadline` | string (date) | No | Fecha límite `YYYY-MM-DD` |
| `is_shared` | boolean | No | Default: `false` |

#### Response — 201 Created

```json
{
  "id": 1,
  "owner_name": "Juan",
  "name": "Viaje a Japón",
  "description": "Ahorro para el viaje de diciembre",
  "target_amount": "5000000.00",
  "current_amount": "0.00",
  "remaining_amount": "5000000.00",
  "currency": "COP",
  "deadline": "2026-12-01",
  "is_shared": false,
  "status": "ACTIVE",
  "progress": 0.0,
  "participants_count": 0,
  "created_at": "2026-07-15T12:00:00-05:00",
  "updated_at": "2026-07-15T12:00:00-05:00"
}
```

> Si `is_shared = true`, el propietario se agrega automáticamente como participante.

---

### GET `/api/savings/goals/`

Lista las metas del usuario autenticado. Incluye:
- Todas las metas propias
- Metas de otros usuarios donde `is_shared = true` y el usuario es participante

**Requiere autenticación.**

#### Response — 200 OK

```json
[
  {
    "id": 1,
    "owner_name": "Juan",
    "name": "Viaje a Japón",
    "description": "Ahorro para el viaje de diciembre",
    "target_amount": "5000000.00",
    "current_amount": "1500000.00",
    "remaining_amount": "3500000.00",
    "currency": "COP",
    "deadline": "2026-12-01",
    "is_shared": false,
    "status": "ACTIVE",
    "progress": 30.0,
    "participants_count": 0,
    "created_at": "2026-07-15T12:00:00-05:00",
    "updated_at": "2026-07-15T14:30:00-05:00"
  }
]
```

> **Campos calculados**:
> - `remaining_amount` = `target_amount` - `current_amount` (mínimo 0)
> - `progress` = porcentaje (0 - 100)
> - `participants_count` = cantidad de participantes

---

### GET `/api/savings/goals/{id}/`

Detalle de una meta de ahorro.

- Si eres el propietario → la ves
- Si eres participante y es compartida → la ves
- Si no tienes acceso → 404

**Requiere autenticación.**

#### Response — 200 OK

Misma estructura que el listado, pero como objeto único:

```json
{
  "id": 1,
  "owner_name": "Juan",
  "name": "Viaje a Japón",
  "description": "Ahorro para el viaje de diciembre",
  "target_amount": "5000000.00",
  "current_amount": "1500000.00",
  "remaining_amount": "3500000.00",
  "currency": "COP",
  "deadline": "2026-12-01",
  "is_shared": false,
  "status": "ACTIVE",
  "progress": 30.0,
  "participants_count": 0,
  "created_at": "2026-07-15T12:00:00-05:00",
  "updated_at": "2026-07-15T14:30:00-05:00"
}
```

#### Errores

| Código | Causa |
|---|---|
| 404 | La meta no existe o no tienes acceso |
| 401 | No autenticado |

---

### PUT `/api/savings/goals/{id}/`

Actualiza una meta de ahorro. Solo el propietario puede actualizar.

**No se puede modificar:** `owner`, `current_amount` (se actualiza vía depósitos/retiros).

**Requiere autenticación.**

#### Request (parcial)

```json
{
  "name": "Casa propia",
  "target_amount": 80000000
}
```

#### Response — 200 OK

Misma estructura que GET detail.

#### Errores

| Código | Causa |
|---|---|
| 403 | No eres el propietario |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### DELETE `/api/savings/goals/{id}/`

Elimina una meta de ahorro. Solo el propietario puede eliminar. Se elimina la meta y todos sus movimientos y participantes en cascada.

**Requiere autenticación.**

#### Response — 204 No Content

Sin body.

#### Errores

| Código | Causa |
|---|---|
| 403 | No eres el propietario |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### POST `/api/savings/goals/{id}/deposit/`

Registra un depósito en una meta. El monto se suma al `current_amount`.

- Solo se puede depositar en metas con status `ACTIVE`
- Si el depósito hace que `current_amount >= target_amount`, la meta cambia a `COMPLETED`
- En metas compartidas, cualquier participante puede depositar

**Requiere autenticación.**

#### Request

```json
{
  "amount": 500000,
  "description": "Ahorro de julio"
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `amount` | number | Sí | Monto a depositar (mínimo 0.01) |
| `description` | string | No | Descripción (default: "") |

#### Response — 201 Created

```json
{
  "detail": "Depósito registrado exitosamente.",
  "movement": {
    "id": 1,
    "user_name": "Juan",
    "type": "DEPOSIT",
    "amount": "500000.00",
    "description": "Ahorro de julio",
    "created_at": "2026-07-15T14:30:00-05:00"
  },
  "goal": {
    "id": 1,
    "owner_name": "Juan",
    "name": "Viaje a Japón",
    "current_amount": "2000000.00",
    "target_amount": "5000000.00",
    "remaining_amount": "3000000.00",
    "progress": 40.0,
    "status": "ACTIVE",
    ...
  }
}
```

#### Errores

| Código | Causa |
|---|---|
| 400 | La meta no está activa (PAUSED/CANCELLED/COMPLETED) |
| 400 | Monto inválido o faltante |
| 403 | No eres propietario ni participante |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### POST `/api/savings/goals/{id}/withdraw/`

Registra un retiro de una meta. El monto se resta al `current_amount`.

- No se permiten retiros que dejen el saldo negativo
- Solo se puede retirar en metas con status `ACTIVE`

**Requiere autenticación.**

#### Request

```json
{
  "amount": 100000,
  "description": "Emergencia"
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `amount` | number | Sí | Monto a retirar (mínimo 0.01) |
| `description` | string | No | Descripción (default: "") |

#### Response — 201 Created

```json
{
  "detail": "Retiro registrado exitosamente.",
  "movement": {
    "id": 2,
    "user_name": "Juan",
    "type": "WITHDRAW",
    "amount": "100000.00",
    "description": "Emergencia",
    "created_at": "2026-07-15T15:00:00-05:00"
  },
  "goal": {
    "id": 1,
    "current_amount": "1900000.00",
    "remaining_amount": "3100000.00",
    "progress": 38.0,
    "status": "ACTIVE",
    ...
  }
}
```

#### Errores

| Código | Causa |
|---|---|
| 400 | Saldo insuficiente (`amount > current_amount`) |
| 400 | La meta no está activa |
| 400 | Monto inválido o faltante |
| 403 | No eres propietario ni participante |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### GET `/api/savings/goals/{id}/movements/`

Historial de movimientos de una meta. Solo el propietario o participantes pueden ver el historial.

**Requiere autenticación.**

#### Response — 200 OK

```json
[
  {
    "id": 2,
    "user_name": "Juan",
    "type": "WITHDRAW",
    "amount": "100000.00",
    "description": "Emergencia",
    "created_at": "2026-07-15T15:00:00-05:00"
  },
  {
    "id": 1,
    "user_name": "Juan",
    "type": "DEPOSIT",
    "amount": "500000.00",
    "description": "Ahorro de julio",
    "created_at": "2026-07-15T14:30:00-05:00"
  }
]
```

> Los movimientos se ordenan del más reciente al más antiguo.

#### Errores

| Código | Causa |
|---|---|
| 403 | No eres propietario ni participante |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### POST `/api/savings/goals/{id}/participants/`

Agrega un usuario como participante de una meta compartida. Solo el propietario puede agregar.

**La meta debe tener `is_shared = true`.**

**Requiere autenticación.**

#### Request

```json
{
  "user_id": 2
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `user_id` | integer | Sí | ID del usuario a agregar |

#### Response — 201 Created

```json
{
  "id": 1,
  "user_name": "María",
  "joined_at": "2026-07-15T16:00:00-05:00"
}
```

#### Errores

| Código | Causa |
|---|---|
| 400 | La meta no es compartida |
| 400 | `user_id` faltante |
| 400 | El usuario no existe |
| 400 | El usuario ya es participante |
| 403 | No eres el propietario |
| 404 | La meta no existe |
| 401 | No autenticado |

---

## Códigos de error

| Código | Significado | Cuándo ocurre |
|---|---|---|
| `200` | OK | Operación exitosa |
| `201` | Created | Recurso creado exitosamente |
| `204` | No Content | Eliminación exitosa (sin body) |
| `400` | Bad Request | Datos inválidos, faltantes o regla de negocio violada |
| `401` | Unauthorized | No autenticado o token inválido/expirado |
| `403` | Forbidden | Autenticado pero sin permiso para esta acción |
| `404` | Not Found | El recurso no existe o no tienes acceso |
| `405` | Method Not Allowed | Método HTTP no permitido (ej: DELETE en gastos) |

### Formato de errores

Siempre retorna un JSON con la clave `detail`:

```json
{
  "detail": "Mensaje descriptivo del error en español"
}
```

Para errores de validación de campos:

```json
{
  "campo": ["Mensaje de error 1", "Mensaje de error 2"]
}
```

---

## Estructuras de datos

### Gasto (Expense)

```typescript
interface Expense {
  id: number;
  usuario_nombre: string;    // Nombre del dueño (read-only)
  categoria: string;
  fecha: string;              // "YYYY-MM-DD"
  descripcion: string;
  valor: string;              // "123456.78"
  compartido: boolean;
  created_at: string;         // "YYYY-MM-DDTHH:MM:SS-05:00"
}
```

### Meta de ahorro (SavingGoal)

```typescript
interface SavingGoal {
  id: number;
  owner_name: string;         // Nombre del propietario (read-only)
  name: string;
  description: string;
  target_amount: string;      // "5000000.00"
  current_amount: string;     // Actualizado vía depósitos/retiros (read-only)
  remaining_amount: string;   // Calculado: target - current (read-only)
  currency: string;           // "COP"
  deadline: string | null;    // "YYYY-MM-DD" o null
  is_shared: boolean;
  status: "ACTIVE" | "COMPLETED" | "PAUSED" | "CANCELLED";
  progress: number;           // 0.0 - 100.0 (read-only)
  participants_count: number; // read-only
  created_at: string;
  updated_at: string;
}
```

### Movimiento de ahorro (SavingMovement)

```typescript
interface SavingMovement {
  id: number;
  user_name: string;          // Nombre de quien hizo el movimiento
  type: "DEPOSIT" | "WITHDRAW" | "ADJUSTMENT";
  amount: string;             // "500000.00"
  description: string;
  created_at: string;
}
```

### Participante (SavingGoalParticipant)

```typescript
interface SavingGoalParticipant {
  id: number;
  user_name: string;
  joined_at: string;
}
```

### Tokens JWT

```typescript
interface TokenResponse {
  access: string;   // Usar en Authorization header
  refresh: string;  // Usar para renovar access token
}
```

---

## Notas para el frontend

### IDs de usuarios

Los IDs de usuario son `1` y `2` (los 2 usuarios únicos de la app). Se obtienen del JWT al activar la cuenta o del campo `user` en la respuesta de `/api/activate-key/`.

### Valores monetarios

Los valores monetarios vienen como **strings** con 2 decimales (ej: `"45000.00"`). En el frontend, parsear a número antes de mostrar:

```javascript
const valorNumerico = parseFloat(expense.valor);
```

### Fechas

Las fechas de tipo `DateField` vienen en formato `YYYY-MM-DD`. Las de tipo `DateTimeField` vienen en formato ISO 8601 con zona horaria (ej: `2026-07-15T12:00:00-05:00`).

### Paginación

La API no tiene paginación implementada actualmente. El listado retorna todos los registros. Para los 2 usuarios del proyecto, esto es suficiente. Si en el futuro se necesita, se agregará paginación offset o cursor.

### CORS

El backend NO tiene CORS configurado actualmente. Cuando se desarrolle el frontend, se necesitará agregar `django-cors-headers` al backend para permitir peticiones desde el dominio del frontend.
