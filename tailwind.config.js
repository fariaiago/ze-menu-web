/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
	'./templates/*.html',
	],
	theme: {
		fontFamily: {
			'sans': ['"Open Sans"', 'sans-serif']
		},
		extend: {
			colors: {
			"ze-verde1": "#14C871",
			"ze-verde2": "#53E883",
			"ze-sucesso": "#2CB859",
			"ze-aviso": "#EAC648",
			"ze-erro": "#E75858",
			"ze-fdark": "#BFBFBF",
			},
			animation: {
				fade: 'fadeOut 10s ease-in-out forwards',
			},
			keyframes: theme => ({
				fadeOut: {
					'0%': { opacity: 1 },
					'100%': { opacity: 0, visibility: 'hidden' },
				},
			}),
		},
	},
	plugins: [],
}

