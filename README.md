# proctextadventure


This little project is about trying to take an important game genre from my childhood, text adventures, and applying the idea of procedural generation so that the game is different each time it's played.

The data file branches first at thematic genres, and this is the primary future expansion point once the conditions are met with existing genre data, such that a bewildering array of genres will be part of the game; the first four which stubbed out are fantasy, sci-fi, post-apocalyptic, and western. To be considered further are: mystery, horror, historical, pirate, steampunk, noir, magical, lovecraftian, espionage, military, zombie, mythology, fairy tale, time travel, gothic, space opera, absurdist/dadaist, underwater exploration, alien invasion, heist, samurai, ninja, prehistoric, Biblical, robot uprising, and we could really go on for quite a while, couldn't we?

In the immediate next big implementation I will try to add in the experience/level and turn-based combat system, which were working very nicely in a previous version that I catastrophically destroyed and need to be rebuilt. 

The game loop will eventually be something like this (as currently imagined): traverse the map to find the key item, fighting enemies and gaining levels, finding stat-boosting armor and weapons, adding allies to your party, and then, when each "small" 9x9 map has been resolved, throwing the player into a new, similarly designed map starting all the way from a random genre, increase the level of the newly created enemies, and then just play with the math until the combat/leveling is fun and see what else it needs.

7.2.23 *** One thing I've discovered to be very helpful is to maintain a list of the exact requirements under which useful data can be created for the game. Each distinct object in the structure needs a very careful definition to try and minimize "unrealism" as they'll all be combined together with other randomly selected objects.

For room "names":
1. The room names should logically fit within the general conception of a sub-area or visitable place within or in the immediate locality of the prompted location.
2. Room names should prioritize adhering to the genre and setting, without the inclusion of any adjectives or modifiers. Additional dimensions can be added later.
3. Keep the room names simple, utilizing words that are synonymous with or well-known and recognizable parts of the given prompt location or area type.
4. Adjectives should not be used in the room names, as they will not be included.
5. The room names should provide a broad variety of simple words that reflect different areas or sub-areas within the prompted location.
6. Format the output as a JSON-type array of comma-separated strings of room names.

For adjectives:
1. Ordinary Universal Adjectives: Include 10 general adjectives that could describe any room, not specific to the genre or room type. These should be common descriptors that capture basic features, such as size, brightness, temperature, etc.
2. Room Universality: The adjectives should not only be applicable to the given room type, but also be fitting for potential sub-areas within the room type. This means that the adjectives should be universal enough to describe any plausible subregion within the broader area defined by the room type.
3. Genre Influence: Include genre-specific adjectives to provide the specific atmosphere. These should be words that are often associated with the genre and help build a mental picture of it. For example, 'post-apocalyptic' could inspire words like 'ruined', 'desolate', 'abandoned'.
4. Adjective Complexity & Connotation: Ensure a mix of positive, negative, and neutral descriptors, avoiding any overly exaggerated or unfitting terms. This involves avoiding words that would be too extreme for the room type or not align with the genre.
5. Compound Frequency & Type-specificity: Include a mix of single-word and compound adjectives, with some specifically suitable for the room environment. These should not dominate the list but rather provide additional variety and richness to the description.
6. The total number of adjectives generated per room type and genre should be 30, with one-third being ordinary universal adjectives and the rest being a blend of room-specific and genre-specific adjectives.
7. Output Format: The generated adjectives should be output as a JSON array of strings. Each string represents a single adjective or a compound adjective. The total number of adjectives in the array should be 30, with one-third being ordinary universal adjectives and the rest being a blend of room-specific and genre-specific adjectives.

For scenic descriptions:
1. Avoid Specific References: Describe the scenic objects or elements without directly mentioning specific room types, areas, or prompt-related words.
2. Diverse Sentence Structures: Use a variety of sentence structures to bring variety and interest to the descriptions.
3. Stay within the Genre: Ensure that the descriptions align with the overall thematic subject, such as the post-apocalyptic genre.
4. Compatibility with Theme: Maintain compatibility with the overall theme by depicting the appropriate atmosphere, mood, and ambiance.
5. Logical Consistency: Avoid referencing objects or elements that contradict the logic of the other rules or break the immersion of the scene.
6. Omit Time References: Do not mention the time of day by referencing the sun, moon, or stars in order to maintain a timeless quality.
7. Formatting: Format the output as a JSON array of comma-separated string values in quotes.

For atmospheric descriptions:
1. Describe the atmosphere in a moody, dramatic, and evocative manner, focusing on the reader's feelings within that place.
2. The generated statement constitutes the whole atmosphere, with scenic elements provided elsewhere.
3. Use non-visual sensory descriptions to evoke a strong sense of atmosphere, including smell, taste, sound, and feeling.
4. Be vivid, detailed, and expressive in the descriptions without being ostentatious or flowery.
5. Avoid referencing specific scenic objects or elements and refrain from mentioning the time of day.
6. Ensure the descriptions adhere to the specified genre and room type in the prompt.
7. Capture the relevant states of disrepair, abandonment, or other atmospheres associated with the genre and room type.
8. Avoid referencing objects or elements that transgress the logic of the other rules.
9. Format the output as a JSON array of comma-separated string values in quotes.



