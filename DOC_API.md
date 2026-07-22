# Documentacion API - Finanzas

Guia completa de la API REST.

**Base URL:** `http://127.0.0.1:8000/api/`

---

## Tabla de contenido

- [Autenticacion](#autenticacion)
  - [Flujo de activacion](#flujo-de-activacion)
  - [Como usar el JWT](#como-usar-el-jwt)
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
- [Codigos de error](#codigos-de-error)
- [Estructuras de datos](#estructuras-de-datos)

---

## Autenticacion

### Flujo de activacion

```
1. Cliente envia POST /api/activate-key/ con { key, name }
2. Backend valida la llave
3. Si es valida -> crea el usuario + retorna JWT
4. Si no es valida -> retorna error 400
```

**Despues de activar, el usuario NUNCA necesita hacer login de nuevo** — el JWT se renueva con el refresh token.

### Como usar el JWT

Incluir el token en cada peticion autenticada:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Ejemplo con curl:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
     http://127.0.0.1:8000/api/expenses/
```

### Refresh token

- **Access token**: 60 min de vida (configurable)
- **Refresh token**: 7 dias de vida

Cuando el access token expira, usar el refresh token para obtener uno nuevo.

---

## Endpoints

---

### POST `/api/activate-key/`

Activa una llave de acceso, crea la cuenta de usuario y retorna JWT.

**No requiere autenticacion.**

#### Request

```json
{
  "key": "FINANZAS-2026-USUARIO-1",
  "name": "Juan"
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `key` | string | Si | Llave de activacion |
| `name` | string | Si | Nombre del usuario |

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

| Codigo | Body | Causa |
|---|---|---|
| 400 | `{"detail": "La llave ingresada no es valida."}` | La llave no existe en la BD |
| 400 | `{"detail": "La llave ya fue utilizada anteriormente."}` | La llave ya fue activada |
| 400 | `{"key": ["Este campo es requerido."]}` | Falta el campo `key` |
| 400 | `{"name": ["Este campo es requerido."]}` | Falta el campo `name` |

---

### POST `/api/expenses/`

Crea un nuevo gasto. El `usuario` se obtiene automaticamente del JWT.

**Requiere autenticacion.**

#### Request

```json
{
  "categoria": "Alimentacion",
  "fecha": "2026-07-15",
  "descripcion": "Almuerzo en restaurante",
  "valor": 45000,
  "compartido": false
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `categoria` | string | Si | Categoria del gasto (max 100 caracteres) |
| `fecha` | string (date) | Si | Fecha del gasto. Formato: `YYYY-MM-DD` |
| `descripcion` | string | Si | Descripcion (max 255 caracteres) |
| `valor` | number | Si | Valor monetario (hasta 12 digitos, 2 decimales) |
| `compartido` | boolean | No | Default: `false` |

#### Response — 201 Created

```json
{
  "id": 1,
  "usuario_nombre": "Juan",
  "categoria": "Alimentacion",
  "fecha": "2026-07-15",
  "descripcion": "Almuerzo en restaurante",
  "valor": "45000.00",
  "compartido": false,
  "created_at": "2026-07-15T12:00:00-05:00"
}
```

#### Errores

| Codigo | Causa |
|---|---|
| 401 | No autenticado / token invalido |
| 400 | Campos faltantes o invalidos |

---

### GET `/api/expenses/`

Lista los gastos del usuario autenticado. Incluye:
- Todos los gastos propios
- Gastos de otros usuarios donde `compartido = true`

**Requiere autenticacion.**

#### Response — 200 OK

```json
[
  {
    "id": 1,
    "usuario_nombre": "Juan",
    "categoria": "Alimentacion",
    "fecha": "2026-07-15",
    "descripcion": "Almuerzo en restaurante",
    "valor": "45000.00",
    "compartido": false,
    "created_at": "2026-07-15T12:00:00-05:00"
  },
  {
    "id": 2,
    "usuario_nombre": "Maria",
    "categoria": "Transporte",
    "fecha": "2026-07-14",
    "descripcion": "Uber al trabajo",
    "valor": "12000.00",
    "compartido": true,
    "created_at": "2026-07-14T08:30:00-05:00"
  }
]
```

> **Nota**: Los gastos compartidos muestran el `usuario_nombre` del dueno original.

---

### GET `/api/expenses/{id}/`

Obtiene el detalle de un gasto especifico.

- Si es tu gasto -> lo ves
- Si es gasto de otro usuario y es compartido -> lo ves
- Si es gasto de otro usuario y NO es compartido -> 404

**Requiere autenticacion.**

#### Response — 200 OK

```json
{
  "id": 1,
  "usuario_nombre": "Juan",
  "categoria": "Alimentacion",
  "fecha": "2026-07-15",
  "descripcion": "Almuerzo en restaurante",
  "valor": "45000.00",
  "compartido": false,
  "created_at": "2026-07-15T12:00:00-05:00"
}
```

#### Errores

| Codigo | Causa |
|---|---|
| 404 | El gasto no existe o no tienes acceso |
| 401 | No autenticado |

---

### PUT `/api/expenses/{id}/`

Actualiza un gasto. Solo el propietario puede actualizar. Se puede enviar solo los campos que se quieren modificar (partial update).

**Requiere autenticacion.**

#### Request (parcial)

```json
{
  "valor": 50000,
  "compartido": true
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `categoria` | string | No | Categoria |
| `fecha` | string (date) | No | Fecha `YYYY-MM-DD` |
| `descripcion` | string | No | Descripcion |
| `valor` | number | No | Valor monetario |
| `compartido` | boolean | No | Visibilidad |

#### Response — 200 OK

```json
{
  "id": 1,
  "usuario_nombre": "Juan",
  "categoria": "Alimentacion",
  "fecha": "2026-07-15",
  "descripcion": "Almuerzo en restaurante",
  "valor": "50000.00",
  "compartido": true,
  "created_at": "2026-07-15T12:00:00-05:00"
}
```

#### Errores

| Codigo | Causa |
|---|---|
| 403 | Intentas editar un gasto de otro usuario |
| 404 | El gasto no existe o no es tuyo |
| 401 | No autenticado |

---

### POST `/api/savings/goals/`

Crea una meta de ahorro. El usuario autenticado es el propietario.

**Requiere autenticacion.**

#### Request

```json
{
  "name": "Viaje a Japon",
  "description": "Ahorro para el viaje de diciembre",
  "target_amount": 5000000,
  "currency": "COP",
  "deadline": "2026-12-01",
  "is_shared": false
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `name` | string | Si | Nombre de la meta (max 255) |
| `description` | string | No | Descripcion (default: "") |
| `target_amount` | number | Si | Monto objetivo (max 15 digitos, 2 decimales, minimo 0.01) |
| `currency` | string | No | Moneda (default: "COP") |
| `deadline` | string (date) | No | Fecha limite `YYYY-MM-DD` |
| `is_shared` | boolean | No | Default: `false` |

#### Response — 201 Created

```json
{
  "id": 1,
  "owner_name": "Juan",
  "name": "Viaje a Japon",
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

> Si `is_shared = true`, el propietario se agrega automaticamente como participante.

---

### GET `/api/savings/goals/`

Lista las metas del usuario autenticado. Incluye:
- Todas las metas propias
- Metas de otros usuarios donde `is_shared = true` y el usuario es participante

**Requiere autenticacion.**

#### Response — 200 OK

```json
[
  {
    "id": 1,
    "owner_name": "Juan",
    "name": "Viaje a Japon",
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
> - `remaining_amount` = `target_amount` - `current_amount` (minimo 0)
> - `progress` = porcentaje (0 - 100)
> - `participants_count` = cantidad de participantes

---

### GET `/api/savings/goals/{id}/`

Detalle de una meta de ahorro.

- Si eres el propietario -> la ves
- Si eres participante y es compartida -> la ves
- Si no tienes acceso -> 404

**Requiere autenticacion.**

#### Response — 200 OK

Misma estructura que el listado, pero como objeto unico.

#### Errores

| Codigo | Causa |
|---|---|
| 404 | La meta no existe o no tienes acceso |
| 401 | No autenticado |

---

### PUT `/api/savings/goals/{id}/`

Actualiza una meta de ahorro. Solo el propietario puede actualizar.

**No se puede modificar:** `owner`, `current_amount` (se actualiza via depositos/retiros).

**Requiere autenticacion.**

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

| Codigo | Causa |
|---|---|
| 403 | No eres el propietario |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### DELETE `/api/savings/goals/{id}/`

Elimina una meta de ahorro. Solo el propietario puede eliminar. Se elimina la meta y todos sus movimientos y participantes en cascada.

**Requiere autenticacion.**

#### Response — 204 No Content

Sin body.

#### Errores

| Codigo | Causa |
|---|---|
| 403 | No eres el propietario |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### POST `/api/savings/goals/{id}/deposit/`

Registra un deposito en una meta. El monto se suma al `current_amount`.

- Solo se puede depositar en metas con status `ACTIVE`
- Si el deposito hace que `current_amount >= target_amount`, la meta cambia a `COMPLETED`
- En metas compartidas, cualquier participante puede depositar

**Requiere autenticacion.**

#### Request

```json
{
  "amount": 500000,
  "description": "Ahorro de julio"
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `amount` | number | Si | Monto a depositar (minimo 0.01) |
| `description` | string | No | Descripcion (default: "") |

#### Response — 201 Created

```json
{
  "detail": "Deposito registrado exitosamente.",
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
    "name": "Viaje a Japon",
    "current_amount": "2000000.00",
    "target_amount": "5000000.00",
    "remaining_amount": "3000000.00",
    "progress": 40.0,
    "status": "ACTIVE"
  }
}
```

#### Errores

| Codigo | Causa |
|---|---|
| 400 | La meta no esta activa (PAUSED/CANCELLED/COMPLETED) |
| 400 | Monto invalido o faltante |
| 403 | No eres propietario ni participante |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### POST `/api/savings/goals/{id}/withdraw/`

Registra un retiro de una meta. El monto se resta al `current_amount`.

- No se permiten retiros que dejen el saldo negativo
- Solo se puede retirar en metas con status `ACTIVE`

**Requiere autenticacion.**

#### Request

```json
{
  "amount": 100000,
  "description": "Emergencia"
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `amount` | number | Si | Monto a retirar (minimo 0.01) |
| `description` | string | No | Descripcion (default: "") |

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
    "status": "ACTIVE"
  }
}
```

#### Errores

| Codigo | Causa |
|---|---|
| 400 | Saldo insuficiente (`amount > current_amount`) |
| 400 | La meta no esta activa |
| 400 | Monto invalido o faltante |
| 403 | No eres propietario ni participante |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### GET `/api/savings/goals/{id}/movements/`

Historial de movimientos de una meta. Solo el propietario o participantes pueden ver el historial.

**Requiere autenticacion.**

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

> Los movimientos se ordenan del mas reciente al mas antiguo.

#### Errores

| Codigo | Causa |
|---|---|
| 403 | No eres propietario ni participante |
| 404 | La meta no existe |
| 401 | No autenticado |

---

### POST `/api/savings/goals/{id}/participants/`

Agrega un usuario como participante de una meta compartida. Solo el propietario puede agregar.

**La meta debe tener `is_shared = true`.**

**Requiere autenticacion.**

#### Request

```json
{
  "user_id": 2
}
```

| Campo | Tipo | Requerido | Descripcion |
|---|---|---|---|
| `user_id` | integer | Si | ID del usuario a agregar |

#### Response — 201 Created

```json
{
  "id": 1,
  "user_name": "Maria",
  "joined_at": "2026-07-15T16:00:00-05:00"
}
```

#### Errores

| Codigo | Causa |
|---|---|
| 400 | La meta no es compartida |
| 400 | `user_id` faltante |
| 400 | El usuario no existe |
| 400 | El usuario ya es participante |
| 403 | No eres el propietario |
| 404 | La meta no existe |
| 401 | No autenticado |

---

## Codigos de error

| Codigo | Significado | Cuando ocurre |
|---|---|---|
| `200` | OK | Operacion exitosa |
| `201` | Created | Recurso creado exitosamente |
| `204` | No Content | Eliminacion exitosa (sin body) |
| `400` | Bad Request | Datos invalidos, faltantes o regla de negocio violada |
| `401` | Unauthorized | No autenticado o token invalido/expirado |
| `403` | Forbidden | Autenticado pero sin permiso para esta accion |
| `404` | Not Found | El recurso no existe o no tienes acceso |
| `405` | Method Not Allowed | Metodo HTTP no permitido (ej: DELETE en gastos) |

### Formato de errores

Siempre retorna un JSON con la clave `detail`:

```json
{
  "detail": "Mensaje descriptivo del error en espanol"
}
```

Para errores de validacion de campos:

```json
{
  "campo": ["Mensaje de error 1", "Mensaje de error 2"]
}
```

---

## Estructuras de datos

### Gasto (Expense)

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | integer | ID unico del gasto |
| `usuario_nombre` | string | Nombre del dueno (solo lectura) |
| `categoria` | string | Categoria del gasto |
| `fecha` | string | Fecha `YYYY-MM-DD` |
| `descripcion` | string | Descripcion del gasto |
| `valor` | string | Valor monetario `"123456.78"` |
| `compartido` | boolean | Visibilidad compartida |
| `created_at` | string | Fecha de creacion ISO 8601 |

### Meta de ahorro (SavingGoal)

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | integer | ID unico de la meta |
| `owner_name` | string | Nombre del propietario (solo lectura) |
| `name` | string | Nombre de la meta |
| `description` | string | Descripcion |
| `target_amount` | string | Monto objetivo `"5000000.00"` |
| `current_amount` | string | Monto actual (solo lectura) |
| `remaining_amount` | string | Calculado: target - current (solo lectura) |
| `currency` | string | Moneda `"COP"` |
| `deadline` | string/null | Fecha limite `YYYY-MM-DD` o null |
| `is_shared` | boolean | Meta compartida |
| `status` | string | `ACTIVE` / `COMPLETED` / `PAUSED` / `CANCELLED` |
| `progress` | number | Porcentaje 0.0 - 100.0 (solo lectura) |
| `participants_count` | integer | Cantidad de participantes (solo lectura) |
| `created_at` | string | Fecha de creacion ISO 8601 |
| `updated_at` | string | Fecha de actualizacion ISO 8601 |

### Movimiento de ahorro (SavingMovement)

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | integer | ID unico del movimiento |
| `user_name` | string | Nombre de quien hizo el movimiento |
| `type` | string | `DEPOSIT` / `WITHDRAW` / `ADJUSTMENT` |
| `amount` | string | Monto `"500000.00"` |
| `description` | string | Descripcion |
| `created_at` | string | Fecha de creacion ISO 8601 |

### Participante (SavingGoalParticipant)

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | integer | ID unico del participante |
| `user_name` | string | Nombre del usuario |
| `joined_at` | string | Fecha de加入 ISO 8601 |

### Tokens JWT

| Campo | Tipo | Descripcion |
|---|---|---|
| `access` | string | Token de acceso (usar en Authorization header) |
| `refresh` | string | Token de refresco (usar para renovar access token) |

---

## Notas generales

### IDs de usuarios

Los IDs de usuario son `1` y `2` (los 2 usuarios unicos). Se obtienen del JWT al activar la cuenta o del campo `user` en la respuesta de `/api/activate-key/`.

### Valores monetarios

Los valores monetarios vienen como **strings** con 2 decimales (ej: `"45000.00"`). Parsear a numero antes de usar en calculos.

### Fechas

Las fechas de tipo `DateField` vienen en formato `YYYY-MM-DD`. Las de tipo `DateTimeField` vienen en formato ISO 8601 con zona horaria (ej: `2026-07-15T12:00:00-05:00`).

### Paginacion

La API no tiene paginacion implementada actualmente. El listado retorna todos los registros. Para los 2 usuarios del proyecto, esto es suficiente.
