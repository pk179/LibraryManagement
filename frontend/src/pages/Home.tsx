function Home() {
    const username = localStorage.getItem('username');

    return (
        <div>
            <h2>Welcome{username ? `, ${username}` : ''}!</h2>
            <p>This is the library app homepage.</p>
        </div>
    );
}

export default Home;
