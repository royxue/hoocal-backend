//
//  SignInViewModel.h
//  hooCal
//
//  Created by zhongtoby on 14/11/15.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "NetManager.h"

@interface SignInViewModel : NSObject
+ (void)signWithEmail:(NSString *)email Psw:(NSString *)psw Block:(StateBlock)block;
@end
