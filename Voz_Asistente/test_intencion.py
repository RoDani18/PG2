import unittest
from unittest.mock import patch
from Voz_Asistente.intencion import detectar_intencion

class TestDeteccionIntencion(unittest.TestCase):

    @patch("Voz_Asistente.intencion.requests.post")
    def test_respuesta_valida(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "intencion": "consultar_inventario",
            "confianza": 0.85
        }

        intencion, confianza = detectar_intencion("Quiero ver el inventario")
        self.assertEqual(intencion, "consultar_inventario")
        self.assertAlmostEqual(confianza, 0.85)

    @patch("Voz_Asistente.intencion.requests.post")
    def test_respuesta_sin_confianza(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "intencion": "consultar_inventario"
        }

        intencion, confianza = detectar_intencion("Ver inventario")
        self.assertEqual(intencion, "consultar_inventario")
        self.assertEqual(confianza, 0.0)

    @patch("Voz_Asistente.intencion.requests.post")
    def test_error_http(self, mock_post):
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {}

        intencion, confianza = detectar_intencion("Ver inventario")
        self.assertEqual(intencion, "intención_desconocida")
        self.assertEqual(confianza, 0.0)

    @patch("Voz_Asistente.intencion.requests.post")
    def test_excepcion_conexion(self, mock_post):
        mock_post.side_effect = Exception("Servidor no disponible")

        intencion, confianza = detectar_intencion("Ver inventario")
        self.assertEqual(intencion, "intención_desconocida")
        self.assertEqual(confianza, 0.0)

if __name__ == "__main__":
    unittest.main()
