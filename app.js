const API_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
    cargarLibros();
    cargarUsuarios();
    cargarPrestamosActivos();

    const formLibro = document.getElementById("form-libro");
    if (formLibro) {
        formLibro.addEventListener("submit", registrarLibro);
    }

    const formUsuario = document.getElementById("form-usuario");
    if (formUsuario) {
        formUsuario.addEventListener("submit", registrarUsuario);
    }
});

// -------------------------------------------------------------------
// 1. Gestión de Libros / Catálogo
// -------------------------------------------------------------------
async function cargarLibros(consulta = "") {
    try {
        let url = `${API_URL}/libros/buscar`;
        if (consulta) {
            url += `?q=${encodeURIComponent(consulta)}`;
        }

        const respuesta = await fetch(url);
        if (!respuesta.ok) throw new Error("Error al consultar libros");

        const libros = await respuesta.json();
        renderizarTablaLibros(libros);
    } catch (error) {
        console.error("Error al cargar libros:", error);
    }
}

function renderizarTablaLibros(libros) {
    const tbody = document.getElementById("tabla-libros");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!Array.isArray(libros) || libros.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No se encontraron libros.</td></tr>`;
        return;
    }

    libros.forEach(libro => {
        const fila = document.createElement("tr");
        const estaDisponible = libro.ejemplares_disponibles > 0;
        const badgeClass = estaDisponible ? "badge-available" : "badge-empty";

        fila.innerHTML = `
            <td>#${libro.id}</td>
            <td><strong>${libro.titulo}</strong></td>
            <td>${libro.autor}</td>
            <td>${libro.categoria}</td>
            <td>
                <span class="badge ${badgeClass}">
                    ${libro.ejemplares_disponibles} / ${libro.ejemplares_totales}
                </span>
            </td>
            <td>
                ${estaDisponible 
                    ? `<button onclick="solicitarPrestamo(${libro.id})" class="btn-action btn-green">Prestar</button>`
                    : `<button onclick="solicitarReserva(${libro.id})" class="btn-action btn-yellow">Reservar</button>`
                }
            </td>
        `;
        tbody.appendChild(fila);
    });
}

async function registrarLibro(event) {
    event.preventDefault();

    const titulo = document.getElementById("titulo").value;
    const autor = document.getElementById("autor").value;
    const categoria = document.getElementById("categoria").value;
    const ejemplares = parseInt(document.getElementById("ejemplares").value);

    try {
        const url = `${API_URL}/libros?titulo=${encodeURIComponent(titulo)}&autor=${encodeURIComponent(autor)}&categoria=${encodeURIComponent(categoria)}&ejemplares=${ejemplares}`;
        const respuesta = await fetch(url, { method: "POST" });

        if (respuesta.ok) {
            alert("¡Libro registrado con éxito!");
            document.getElementById("form-libro").reset();
            cargarLibros();
        } else {
            alert("Error al guardar el libro.");
        }
    } catch (error) {
        console.error("Error al registrar libro:", error);
    }
}

function filtrarLibros() {
    const inputBuscar = document.getElementById("buscar");
    if (inputBuscar) {
        cargarLibros(inputBuscar.value);
    }
}

// -------------------------------------------------------------------
// 2. Gestión de Usuarios
// -------------------------------------------------------------------
async function cargarUsuarios() {
    try {
        const respuesta = await fetch(`${API_URL}/usuarios`);
        if (!respuesta.ok) throw new Error("Error al consultar usuarios");

        const usuarios = await respuesta.json();
        renderizarTablaUsuarios(usuarios);
    } catch (error) {
        console.error("Error al cargar usuarios:", error);
    }
}

function renderizarTablaUsuarios(usuarios) {
    const tbody = document.getElementById("tabla-usuarios");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!Array.isArray(usuarios) || usuarios.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">No hay usuarios registrados.</td></tr>`;
        return;
    }

    usuarios.forEach(u => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td>#${u.id}</td>
            <td>${u.nombre}</td>
            <td>${u.email}</td>
            <td><span class="badge badge-available">${u.rol}</span></td>
        `;
        tbody.appendChild(fila);
    });
}

async function registrarUsuario(event) {
    event.preventDefault();

    const nombre = document.getElementById("nombre-usuario").value;
    const email = document.getElementById("email-usuario").value;
    const rol = document.getElementById("rol-usuario").value;

    try {
        const url = `${API_URL}/usuarios?nombre=${encodeURIComponent(nombre)}&email=${encodeURIComponent(email)}&rol=${encodeURIComponent(rol)}`;
        const respuesta = await fetch(url, { method: "POST" });

        if (respuesta.ok) {
            const usuario = await respuesta.json();
            alert(`¡Usuario registrado con éxito! ID asignado: #${usuario.id}`);
            document.getElementById("form-usuario").reset();
            cargarUsuarios();
        } else {
            const error = await respuesta.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error("Error al registrar usuario:", error);
    }
}

// -------------------------------------------------------------------
// 3. Préstamos y Devoluciones
// -------------------------------------------------------------------
async function solicitarPrestamo(libroId) {
    const usuarioId = prompt("Ingresa el ID del usuario/socio que solicita el préstamo:");
    if (!usuarioId) return;

    try {
        const respuesta = await fetch(`${API_URL}/prestamos?usuario_id=${usuarioId}&libro_id=${libroId}&dias_prestamo=7`, {
            method: "POST"
        });

        if (respuesta.ok) {
            alert("¡Préstamo registrado con éxito!");
            cargarLibros();
            cargarPrestamosActivos();
        } else {
            const error = await respuesta.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error("Error al procesar préstamo:", error);
    }
}

async function cargarPrestamosActivos() {
    try {
        const respuesta = await fetch(`${API_URL}/reportes/prestamos-activos`);
        if (!respuesta.ok) throw new Error("Error al consultar préstamos activos");

        const prestamos = await respuesta.json();
        renderizarTablaPrestamos(prestamos);
    } catch (error) {
        console.error("Error al cargar préstamos activos:", error);
    }
}

function renderizarTablaPrestamos(prestamos) {
    const tbody = document.getElementById("tabla-prestamos");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!Array.isArray(prestamos) || prestamos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;">No hay préstamos activos en este momento.</td></tr>`;
        return;
    }

    prestamos.forEach(p => {
        const fila = document.createElement("tr");
        const fechaPrestamo = new Date(p.fecha_prestamo).toLocaleDateString();
        const fechaEstimada = new Date(p.fecha_dev_estimada).toLocaleDateString();

        fila.innerHTML = `
            <td>#${p.id}</td>
            <td>Usuario #${p.usuario_id}</td>
            <td>Libro #${p.libro_id}</td>
            <td>${fechaPrestamo}</td>
            <td>${fechaEstimada}</td>
            <td><span class="badge badge-available">${p.estado}</span></td>
            <td>
                <button onclick="devolverLibro(${p.id})" class="btn-action btn-red">
                    Devolver
                </button>
            </td>
        `;
        tbody.appendChild(fila);
    });
}

async function devolverLibro(prestamoId) {
    if (!confirm(`¿Confirmas la devolución del préstamo #${prestamoId}?`)) return;

    try {
        const respuesta = await fetch(`${API_URL}/prestamos/${prestamoId}/devolucion`, {
            method: "POST"
        });

        const resultado = await respuesta.json();

        if (respuesta.ok) {
            if (resultado.multa_generada) {
                alert(`Libro devuelto con retraso. Multa generada: $${resultado.multa_generada}`);
            } else {
                alert(resultado.mensaje);
            }
            cargarLibros();
            cargarPrestamosActivos();
        } else {
            alert(`Error: ${resultado.detail}`);
        }
    } catch (error) {
        console.error("Error al devolver libro:", error);
    }
}

// -------------------------------------------------------------------
// 4. Reservas de Libros
// -------------------------------------------------------------------
async function solicitarReserva(libroId) {
    const usuarioId = prompt("Ingresa el ID del usuario/socio que realiza la reserva:");
    if (!usuarioId) return;

    try {
        const respuesta = await fetch(`${API_URL}/reservas?usuario_id=${usuarioId}&libro_id=${libroId}`, {
            method: "POST"
        });

        if (respuesta.ok) {
            alert("¡Libro reservado con éxito!");
        } else {
            const error = await respuesta.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error("Error al reservar libro:", error);
    }
}