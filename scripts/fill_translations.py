import polib

T = {
 "hi": {
  "Dashboard": "डैशबोर्ड", "Notice Board": "सूचना पट्ट", "Log Complaint": "शिकायत दर्ज करें",
  "My Complaints": "मेरी शिकायतें", "Apply for Certificate": "प्रमाणपत्र के लिए आवेदन करें",
  "My Tasks": "मेरे कार्य", "Grievance Workbench": "शिकायत कार्यक्षेत्र",
  "Token Queue": "टोकन कतार", "Assign Work": "कार्य सौंपें", "Analytics": "विश्लेषण",
  "Logout": "लॉग आउट", "Login": "लॉग इन", "Register": "पंजीकरण करें",
  "Go to Dashboard": "डैशबोर्ड पर जाएँ",
  "One window for village grievances, certificates and notices": "गाँव की शिकायतों, प्रमाणपत्रों और सूचनाओं के लिए एक ही खिड़की",
  "Login as": "इस रूप में लॉग इन करें", "Choose your account type to continue": "जारी रखने के लिए अपना खाता प्रकार चुनें",
  "Citizen": "नागरिक", "Staff / Officer": "कर्मचारी / अधिकारी", "Sarpanch / Nagarsevak": "सरपंच / नगरसेवक",
  "Log complaints, apply for certificates, view notices": "शिकायत दर्ज करें, प्रमाणपत्र के लिए आवेदन करें, सूचनाएँ देखें",
  "Handle assigned tasks and grievances": "सौंपे गए कार्य और शिकायतें संभालें",
  "Password + OTP secured login": "पासवर्ड + OTP सुरक्षित लॉग इन",
  "Don't have an account?": "खाता नहीं है?",
 },
 "mr": {
  "Dashboard": "डॅशबोर्ड", "Notice Board": "सूचना फलक", "Log Complaint": "तक्रार नोंदवा",
  "My Complaints": "माझ्या तक्रारी", "Apply for Certificate": "प्रमाणपत्रासाठी अर्ज करा",
  "My Tasks": "माझी कामे", "Grievance Workbench": "तक्रार कार्यक्षेत्र",
  "Token Queue": "टोकन रांग", "Assign Work": "काम सोपवा", "Analytics": "विश्लेषण",
  "Logout": "लॉग आउट", "Login": "लॉग इन", "Register": "नोंदणी करा",
  "Go to Dashboard": "डॅशबोर्डवर जा",
  "One window for village grievances, certificates and notices": "गावातील तक्रारी, प्रमाणपत्रे आणि सूचनांसाठी एकच खिडकी",
  "Login as": "या स्वरूपात लॉग इन करा", "Choose your account type to continue": "पुढे जाण्यासाठी खात्याचा प्रकार निवडा",
  "Citizen": "नागरिक", "Staff / Officer": "कर्मचारी / अधिकारी", "Sarpanch / Nagarsevak": "सरपंच / नगरसेवक",
  "Log complaints, apply for certificates, view notices": "तक्रारी नोंदवा, प्रमाणपत्रासाठी अर्ज करा, सूचना पहा",
  "Handle assigned tasks and grievances": "नेमून दिलेली कामे आणि तक्रारी हाताळा",
  "Password + OTP secured login": "पासवर्ड + OTP सुरक्षित लॉग इन",
  "Don't have an account?": "खाते नाही?",
 },
}
 
from tr_login import T as T_LOGIN
for k in T: T[k].update(T_LOGIN[k])
for lang, words in T.items():
    path = f"locale/{lang}/LC_MESSAGES/django.po"
    po = polib.pofile(path)
    n = 0
    for e in po:
        if e.msgid in words and not e.msgstr:
            e.msgstr = words[e.msgid]
            if "fuzzy" in e.flags:
                e.flags.remove("fuzzy")
            n += 1
    po.save()
    print(lang, "filled", n)
