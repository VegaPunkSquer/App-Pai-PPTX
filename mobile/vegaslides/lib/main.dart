import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'package:vegaslides/provider/auth_provider.dart';
import 'package:vegaslides/provider/theme_provider.dart';

import 'package:vegaslides/services/manifesto.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Manifesto.inicializar(); // A Nave lê o manifesto aqui!
  
  runApp(const VegaSlidesApp());
}

class VegaSlidesApp extends StatelessWidget {
  const VegaSlidesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()), 
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
      ],
      // O Consumer fica vigiando o ThemeProvider o tempo todo
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, child) {
          return MaterialApp(
            title: 'VegaSlides',
            debugShowCheckedModeBanner: false,
            // --- TEMA CLARO --- (Inspirado na sua paleta QPalette do PySide6)
            theme: ThemeData(
              brightness: Brightness.light,
              scaffoldBackgroundColor: const Color(0xFFF0F0F0), // Fundo acinzentado claro
              primaryColor: const Color(0xFF0066CC), // O azul do link do PC
              appBarTheme: const AppBarTheme(
                backgroundColor: Color(0xFFE1E1E1), // AlternateBase do PC
                foregroundColor: Colors.black,
              ),
              colorScheme: const ColorScheme.light(
                primary: Color(0xFF0078D7), // O azul de destaque
                secondary: Color(0xFF8B5CF6),
              ),
              useMaterial3: true,
            ),
            // --- TEMA ESCURO --- (O seu chassi atual)
            darkTheme: ThemeData(
              brightness: Brightness.dark,
              scaffoldBackgroundColor: const Color(0xFF0A0A0A), // Preto profundo Vega
              primaryColor: const Color(0xFF8B5CF6), // Roxo principal
              appBarTheme: const AppBarTheme(
                backgroundColor: Color(0xFF141414),
                foregroundColor: Colors.white,
              ),
              colorScheme: const ColorScheme.dark(
                primary: Color(0xFF8B5CF6),
                secondary: Color(0xFF3B82F6),
              ),
              useMaterial3: true,
            ),
            // O app decide qual usar baseado na variável salva
            themeMode: themeProvider.isDarkMode ? ThemeMode.dark : ThemeMode.light,
            home: const HomeScreen(),
          );
        },
      ),
    );
  }
}