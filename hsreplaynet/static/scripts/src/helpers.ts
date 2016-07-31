export function staticFile(file: string) {
	return STATIC_URL + file;
}

export function joustStaticFile(file: string) {
	return JOUST_STATIC_URL + file;
}

export function image(image: string) {
	return staticFile("images/" + image);
}

export function cardArt(cardArt: string) {
	return joustStaticFile("card-art/" + cardArt) + ".jpg";
}
