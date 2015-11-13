__author__ = 'kkennedy'


def main():
    import labtronyxgui

    controller = labtronyxgui.controllers.MainApplicationController()

    labtronyxgui.wx_views.wx_main.main(controller)

    controller._stop()

if __name__ == '__main__':
    main()