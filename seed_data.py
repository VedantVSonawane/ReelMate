import requests
from app import app
from models import db, Movie

# Curated list of real movies to start with (The "Pro" Move - Instant Value)
INITIAL_MOVIES = [
    {
        "tmdb_id": 27205,
        "title": "Inception",
        "year": 2010,
        "genres": "Action|Sci-Fi|Thriller",
        "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to regain his old life as payment for a task considered to be impossible: \"inception\", the implantation of another person's idea into a target's subconscious.",
        "poster_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
        "platforms": "Netflix|Amazon Prime"
    },
    {
        "tmdb_id": 157336,
        "title": "Interstellar",
        "year": 2014,
        "genres": "Adventure|Drama|Sci-Fi",
        "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
        "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniL6E8AHtMY4kRFW97ngj.jpg",
        "platforms": "Netflix|JioCinema"
    },
    {
        "tmdb_id": 155,
        "title": "The Dark Knight",
        "year": 2008,
        "genres": "Drama|Action|Crime|Thriller",
        "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets. The partnership proves to be effective, but they soon find themselves prey to a reign of chaos unleashed by a rising criminal mastermind known to the terrified citizens of Gotham as the Joker.",
        "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "platforms": "Netflix|JioCinema"
    },
    {
        "tmdb_id": 19995,
        "title": "Avatar",
        "year": 2009,
        "genres": "Action|Adventure|Fantasy|Sci-Fi",
        "overview": "In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission, but becomes torn between following orders and protecting an alien civilization.",
        "poster_url": "https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg",
        "platforms": "Disney+ Hotstar"
    },
    {
        "tmdb_id": 299536,
        "title": "Avengers: Infinity War",
        "year": 2018,
        "genres": "Adventure|Action|Sci-Fi",
        "overview": "As the Avengers and their allies have continued to protect the world from threats too large for any one hero to handle, a new danger has emerged from the cosmic shadows: Thanos. A despot of intergalactic infamy, his goal is to collect all six Infinity Stones, artifacts of unimaginable power, and use them to inflict his twisted will on all of reality. Everything the Avengers have fought for has led up to this moment - the fate of Earth and existence itself has never been more uncertain.",
        "poster_url": "https://image.tmdb.org/t/p/w500/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
        "platforms": "Disney+ Hotstar"
    },
    {
        "tmdb_id": 24428,
        "title": "The Avengers",
        "year": 2012,
        "genres": "Science Fiction|Action|Adventure",
        "overview": "When an unexpected enemy emerges and threatens global safety and security, Nick Fury, director of the international peacekeeping agency known as S.H.I.E.L.D., finds himself in need of a team to pull the world back from the brink of disaster. Spanning the globe, a daring recruitment effort begins!",
        "poster_url": "https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg",
        "platforms": "Disney+ Hotstar"
    },
    {
        "tmdb_id": 496243,
        "title": "Parasite",
        "year": 2019,
        "genres": "Comedy|Thriller|Drama",
        "overview": "All unemployed, Ki-taek's family takes peculiar interest in the wealthy and glamorous Parks for their livelihood until they get entangled in an unexpected incident.",
        "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        "platforms": "SonyLIV"
    },
    {
        "tmdb_id": 372058,
        "title": "Your Name.",
        "year": 2016,
        "genres": "Romance|Animation|Drama",
        "overview": "High schoolers Mitsuha and Taki are complete strangers living separate lives. But one night, they suddenly switch places. Mitsuha wakes up in Taki’s body, and he in hers. This bizarre occurrence continues to happen randomly, and the two must adjust their lives around each other.",
        "poster_url": "https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg",
        "platforms": "Netflix"
    },
    {
        "tmdb_id": 129,
        "title": "Spirited Away",
        "year": 2001,
        "genres": "Animation|Family|Fantasy",
        "overview": "A young girl, Chihiro, becomes trapped in a strange new world of spirits. When her parents undergo a mysterious transformation, she must call upon the courage she never knew she had to free her family.",
        "poster_url": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUKGnSxQb9lf.jpg",
        "platforms": "Netflix"
    },
    {
        "tmdb_id": 634649,
        "title": "Spider-Man: No Way Home",
        "year": 2021,
        "genres": "Action|Adventure|Sci-Fi",
        "overview": "Peter Parker is unmasked and no longer able to separate his normal life from the high-stakes of being a super-hero. When he asks for help from Doctor Strange the stakes become even more dangerous, forcing him to discover what it truly means to be Spider-Man.",
        "poster_url": "https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg",
        "platforms": "Netflix|SonyLIV"
    },
    {
        "tmdb_id": 49026,
        "title": "The Dark Knight Rises",
        "year": 2012,
        "genres": "Action|Crime|Drama|Thriller",
        "overview": "Following the death of District Attorney Harvey Dent, Batman assumes responsibility for Dent's crimes to protect the late attorney's reputation and is subsequently hunted by the Gotham City Police Department. Eight years later, Batman encounters the mysterious Selina Kyle and the villainous Bane, a new terrorist leader who overwhelms Gotham's finest. The Dark Knight resurfaces to protect a city that has branded him an enemy.",
        "poster_url": "https://image.tmdb.org/t/p/w500/85cWkCVftiVs0BV86Gx05AAtEQZ.jpg",
        "platforms": "Netflix|JioCinema"
    },
    {
        "tmdb_id": 680,
        "title": "Pulp Fiction",
        "year": 1994,
        "genres": "Thriller|Crime",
        "overview": "A burger-loving hit man, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that ingeniously trip back and forth in time.",
        "poster_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "platforms": "Amazon Prime"
    },
    {
        "tmdb_id": 13,
        "title": "Forrest Gump",
        "year": 1994,
        "genres": "Comedy|Drama|Romance",
        "overview": "A man with a low IQ has accomplished great things in his life and been present during significant historic events—in each case, far exceeding what anyone imagined he could do. But despite all he has achieved, his one true love eludes him.",
        "poster_url": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
        "platforms": "Netflix|Amazon Prime"
    },
    {
        "tmdb_id": 278,
        "title": "The Shawshank Redemption",
        "year": 1994,
        "genres": "Drama|Crime",
        "overview": "Framed in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison, where he puts his accounting skills to work for an amoral warden. During his long stretch in prison, Dufresne comes to be admired by the other inmates -- including an older prisoner named Red -- for his integrity and unquenchable sense of hope.",
        "poster_url": "https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg",
        "platforms": "Amazon Prime"
    },
    {
        "tmdb_id": 238,
        "title": "The Godfather",
        "year": 1972,
        "genres": "Drama|Crime",
        "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care of the would-be killers, launching a campaign of bloody revenge.",
        "poster_url": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "platforms": "Amazon Prime"
    },
    {
        "tmdb_id": 11,
        "title": "Star Wars",
        "year": 1977,
        "genres": "Adventure|Action|Sci-Fi",
        "overview": "Princess Leia is captured and held hostage by the evil Imperial forces in their effort to take over the galactic Empire. Venturesome Luke Skywalker and dashing captain Han Solo team together with the loveable robot duo R2-D2 and C-3PO to rescue the beautiful princess and restore peace and justice in the Empire.",
        "poster_url": "https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg",
        "platforms": "Disney+ Hotstar"
    },
    {
        "tmdb_id": 550,
        "title": "Fight Club",
        "year": 1999,
        "genres": "Drama",
        "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy. Their concept catches on, with underground \"fight clubs\" forming in every town, until an eccentric gets in the way and ignites an out-of-control spiral toward oblivion.",
        "poster_url": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "platforms": "Amazon Prime"
    },
    {
        "tmdb_id": 603,
        "title": "The Matrix",
        "year": 1999,
        "genres": "Action|Sci-Fi",
        "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.",
        "poster_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpFUk5H.jpg",
        "platforms": "Netflix|JioCinema"
    },
    {
        "tmdb_id": 120,
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "year": 2001,
        "genres": "Adventure|Fantasy|Action",
        "overview": "Young hobbit Frodo Baggins, after inheriting a mysterious ring from his uncle Bilbo, must leave his home in order to keep it from falling into the hands of its evil creator. Along the way, a fellowship is formed to protect the ringbearer and make sure that the ring arrives at its final destination: Mt. Doom, the only place where it can be destroyed.",
        "poster_url": "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
        "platforms": "Amazon Prime"
    },
    {
        "tmdb_id": 121,
        "title": "The Lord of the Rings: The Two Towers",
        "year": 2002,
        "genres": "Adventure|Fantasy|Action",
        "overview": "Frodo and Sam are trekking to Mordor to destroy the One Ring of Power while Gimli, Legolas and Aragorn search for the orc-captured Merry and Pippin. All along, nefarious wizard Saruman awaits the Fellowship members at the Orthanc Tower in Isengard.",
        "poster_url": "https://image.tmdb.org/t/p/w500/5VTN0pR8gcqV3EPUHHfMGnJYN9L.jpg",
        "platforms": "Amazon Prime"
    }
]

def seed_db():
    with app.app_context():
        db.create_all()
        
        # Check if DB is already populated
        if Movie.query.first():
            print("Database already populated.")
            return

        print("Seeding database with real movies...")
        for m in INITIAL_MOVIES:
            movie = Movie(
                tmdb_id=m['tmdb_id'],
                title=m['title'],
                year=m['year'],
                genres=m['genres'],
                overview=m['overview'],
                poster_url=m['poster_url'],
                platforms=m['platforms']
            )
            db.session.add(movie)
        
        db.session.commit()
        print(f"Successfully added {len(INITIAL_MOVIES)} movies!")

def fetch_tmdb_data(api_key):
    """
    Future-proofing: Function to fetch more data if user provides API Key.
    """
    pass

if __name__ == '__main__':
    seed_db()
