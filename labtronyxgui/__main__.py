__author__ = 'kkennedy'

import sys

def main(args=None):

    if args is None:
        args = sys.argv[1:]

    try:
        # from application.a_Main import a_Main
        # main_gui = a_Main()
        # main_gui.mainloop()

        import wx
        app = wx.App()

        import controllers.main
        controller = controllers.main.MainApplicationController()

        import views.wx_main
        view = views.wx_main.MainView(controller)

        app.SetTopWindow(view.frame)
        app.MainLoop()

    except Exception as e:
        raise
        raise EnvironmentError("Unable to load labtronyx-gui")

if __name__ == '__main__':
    main()