import json
from typing import Callable


class Settings:
    """ Class to hold application settings """
    def __init__( self, settings_dict: dict, save_callback: Callable = None ):
        self._save_callback = save_callback
        self._on_top = settings_dict.get( 'on_top', False )
        self._minimize_on_running = settings_dict.get( 'minimize_on_running', False )
        self._send_mail_on_error = settings_dict.get( 'send_mail_on_error', False )
        self._include_ss_in_error_mail = settings_dict.get( 'include_ss_in_error_mail', False )
        self._current_language = settings_dict.get( 'current_language', 'sv_SE' )


    def to_json( self ) -> dict:
        """ Convert settings to a JSON-serializable dictionary """

        d = { k.lstrip( '_' ): v
             for k, v in self.__dict__.items()
             if not callable( self.__dict__[ k ] ) }
        return json.dumps( d, indent = 2 )


    @property
    def current_language( self ):
        """ Property function to get 'current_language' """

        return self.get( 'current_language' )


    @current_language.setter
    def current_language( self, value: bool ):
        """ Property setter function to set 'current_language' """

        self._current_language = value
        if self._save_callback:
            self._save_callback( self )


    @property
    def send_mail_on_error( self ):
        """ Property function to get 'send_mail_on_error' """

        return self.get( 'send_mail_on_error' )


    @send_mail_on_error.setter
    def send_mail_on_error( self, value: bool ):
        """ Property setter function to set 'send_mail_on_error'

        Args:
            value (bool): Value to set
        """

        self._send_mail_on_error = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def include_ss_in_error_mail( self ):
        """ Property function to get 'on_top' """

        return self.get( 'include_ss_in_error_mail' )


    @include_ss_in_error_mail.setter
    def include_ss_in_error_mail( self, value: bool ):
        """ Property setter function to set 'include_ss_in_error_mail'

        Args:
            value (bool): Value to set
        """

        self._include_ss_in_error_mail = value
        if self._save_callback:
            self._save_callback( self )


    @property
    def minimize_on_running( self ):
        """ Property function to get 'on_top' """

        return self.get( 'minimize_on_running' )


    @minimize_on_running.setter
    def minimize_on_running( self, value: bool ):
        """ Property setter function to set 'minimize_on_running' """

        self._minimize_on_running = value
        if self._save_callback:
            self._save_callback( self )


    @property
    def on_top( self ):
        """ Property function to get 'on_top' """

        return self.get( 'on_top' )


    @on_top.setter
    def on_top( self, value: bool ):
        """ Property setter function to set 'on_top' """

        self._on_top = value
        if self._save_callback:
            self._save_callback( self )


    def get( self, key: str ) -> any:
        """ Get attribute with corrected name

        Args:
            key (str): Key of dict
        """

        return getattr( self, f'_{ key }' )
