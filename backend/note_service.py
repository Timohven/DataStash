from backend.note import Note


class NoteService:
    def __init__(self, database):
        self.database = database

    def create_note(self, author, note_type, note_text):
        query = '''
      INSERT INTO notes (author, note_type, text)
      VALUES (:author, :type, :text)
      RETURNING note_id, created_at, author, note_type, text
    '''
        params = {'author': author, 'type': note_type, 'text': note_text}
        results = self.database.execute_query(query, params, write=True)
        return Note(*results[0]) if results else None

    def get_notes_by_author(self, author):
        query = 'SELECT * FROM notes WHERE author = :author'
        params = {'author': author}
        results = self.database.execute_query(query, params)
        return [Note(*row) for row in results]

    def update_note(self, note_id, note_type, note_text):
        query = '''
          UPDATE notes SET text = :text, note_type = :type WHERE note_id = :id RETURNING * 
        '''
        params = {'text': note_text, 'type': note_type , 'id': note_id}
        results = self.database.execute_query(query, params, write=True)
        return Note(*results[0]) if results else None

    def delete_note(self, note_id):
        query = 'DELETE FROM notes WHERE note_id = :id RETURNING *'
        params = {'id': note_id}
        results = self.database.execute_query(query, params, write=True)
        return Note(*results[0]) if results else None
