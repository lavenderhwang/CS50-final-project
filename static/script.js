document.addEventListener('DOMContentLoaded', function () {
	const form = document.getElementById('save-recipe-form');

	if (form) {
		form.addEventListener('submit', function (event) {
			event.preventDefault(); // Prevent the default form submission

			// Create a FormData object from the form
			const formData = new FormData(form);

			fetch('/save_recipe', {
				method: 'POST',
				body: formData,
			})
				.then((response) => {
					if (response.ok) {
						// Optionally perform actions upon successful save
						console.log('Recipe saved successfully');
					} else {
						console.error('Failed to save recipe');
					}
				})

				.catch((error) => {
					console.error('Error:', error);
				});
		});
	}
});
