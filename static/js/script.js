window.parseISOString = function parseISOString(s) {
	var b = s.split(/\D+/);
	return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

window.handleDeleteVenue = function handleDeleteVenue(venueId) {
	fetch(`/venues/${venueId}`, {
		method: "DELETE",
		headers: {
			"Content-Type": "application/json"
		}
	})
		.then(response => {
			return response.json();
		})
		.then(response => {
			if (response.deleted) {
				window.location.href = "/venues";
			}
		})
		.catch(error => {
			console.log(error);
		});
};
